from dataclasses import dataclass
import re

import fitz

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
except ImportError:  # pragma: no cover - dependency is declared in pyproject
    AnalyzerEngine = None
    NlpEngineProvider = None


@dataclass
class RedactionResult:
    redacted_pdf_bytes: bytes
    redacted_text: str
    entity_count: int
    warnings: list[str]


@dataclass(frozen=True)
class WordBox:
    rect: fitz.Rect
    start: int
    end: int


_SPACY_MODELS = ("en_core_web_lg", "en_core_web_md", "en_core_web_sm")
_REGEX_PATTERNS = {
    "EMAIL_ADDRESS": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "PHONE_NUMBER": re.compile(r"(?:(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]*)\d{3}[-.\s]?\d{4})"),
    "US_SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "IDENTIFIER": re.compile(
        r"\b(?:MRN|Medical Record Number|Patient ID|Member ID|Account Number)\s*[:#-]?\s*[A-Za-z0-9-]{4,}\b",
        re.IGNORECASE,
    ),
    "DOB": re.compile(
        r"\b(?:DOB|Date of Birth)\s*[:#-]?\s*(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})\b",
        re.IGNORECASE,
    ),
}


def redact_pdf(pdf_bytes: bytes) -> RedactionResult:
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    analyzer = _build_presidio_analyzer()
    warnings: list[str] = []
    total_entities = 0
    page_texts: list[str] = []

    if analyzer is None:
        warnings.append(
            "Presidio PERSON and LOCATION detection is unavailable because no spaCy English model is installed. "
            "Regex-based redaction still covers emails, phone numbers, SSNs, DOB labels, and common IDs."
        )

    for page in document:
        page_text, word_boxes = _build_page_text(page)
        page_texts.append(page_text)
        if not page_text.strip() or not word_boxes:
            continue

        spans = _collect_entity_spans(page_text, analyzer)
        total_entities += len(spans)
        if not spans:
            continue

        redacted_word_indexes = _word_indexes_for_spans(word_boxes, spans)
        for word_index in sorted(redacted_word_indexes):
            page.add_redact_annot(word_boxes[word_index].rect, fill=(0, 0, 0))

        page.apply_redactions()

    return RedactionResult(
        redacted_pdf_bytes=document.tobytes(garbage=3, deflate=True),
        redacted_text="\n\n".join(text for text in page_texts if text.strip()),
        entity_count=total_entities,
        warnings=warnings,
    )


def _build_presidio_analyzer() -> AnalyzerEngine | None:
    if AnalyzerEngine is None or NlpEngineProvider is None:
        return None

    model_name = next((candidate for candidate in _SPACY_MODELS if _spacy_model_available(candidate)), None)
    if not model_name:
        return None

    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": model_name}],
        }
    )
    return AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en"])


def _spacy_model_available(model_name: str) -> bool:
    try:
        __import__(model_name)
    except ImportError:
        return False
    return True


def _build_page_text(page: fitz.Page) -> tuple[str, list[WordBox]]:
    words = page.get_text("words", sort=True)
    parts: list[str] = []
    word_boxes: list[WordBox] = []
    position = 0
    current_line: tuple[int, int] | None = None

    for x0, y0, x1, y1, text, block_no, line_no, _word_no in words:
        line_key = (block_no, line_no)
        if word_boxes:
            separator = "\n" if line_key != current_line else " "
            parts.append(separator)
            position += len(separator)

        start = position
        parts.append(text)
        position += len(text)
        word_boxes.append(WordBox(rect=fitz.Rect(x0, y0, x1, y1), start=start, end=position))
        current_line = line_key

    return "".join(parts), word_boxes


def _collect_entity_spans(text: str, analyzer: AnalyzerEngine | None) -> list[tuple[int, int]]:
    spans = _regex_spans(text)
    if analyzer is not None:
        presidio_results = analyzer.analyze(
            text=text,
            language="en",
            entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "US_SSN", "LOCATION"],
        )
        spans.extend((result.start, result.end) for result in presidio_results)
    return _merge_spans(spans)


def _regex_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for pattern in _REGEX_PATTERNS.values():
        spans.extend((match.start(), match.end()) for match in pattern.finditer(text))
    return spans


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []

    ordered_spans = sorted(spans)
    merged = [ordered_spans[0]]
    for start, end in ordered_spans[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def _word_indexes_for_spans(word_boxes: list[WordBox], spans: list[tuple[int, int]]) -> set[int]:
    indexes: set[int] = set()
    for span_start, span_end in spans:
        for index, word_box in enumerate(word_boxes):
            if word_box.end <= span_start:
                continue
            if word_box.start >= span_end:
                break
            indexes.add(index)
    return indexes
