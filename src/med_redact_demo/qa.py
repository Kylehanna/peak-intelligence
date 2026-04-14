import math
import re

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from med_redact_demo.config import settings


def answer_question(document_text: str, question: str) -> str:
    chunks = _split_document(document_text)
    if not chunks:
        return "No text was extracted from the redacted document."

    if settings.openai_api_key:
        relevant_chunks = _retrieve_with_embeddings(chunks, question)
        return _answer_with_model(relevant_chunks, question)

    relevant_chunks = _retrieve_with_keywords(chunks, question)
    excerpt_block = "\n\n".join(f"Excerpt {index + 1}:\n{chunk}" for index, chunk in enumerate(relevant_chunks))
    return (
        "OPENAI_API_KEY is not configured, so the app is returning the most relevant excerpts instead of a synthesized answer.\n\n"
        f"{excerpt_block}"
    )


def _split_document(document_text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return [chunk.strip() for chunk in splitter.split_text(document_text) if chunk.strip()]


def _retrieve_with_embeddings(chunks: list[str], question: str, limit: int = 4) -> list[str]:
    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )
    chunk_vectors = embeddings.embed_documents(chunks)
    query_vector = embeddings.embed_query(question)
    scored_chunks = [
        (_cosine_similarity(query_vector, chunk_vector), chunk)
        for chunk, chunk_vector in zip(chunks, chunk_vectors, strict=True)
    ]
    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _score, chunk in scored_chunks[:limit]]


def _retrieve_with_keywords(chunks: list[str], question: str, limit: int = 4) -> list[str]:
    query_terms = _tokenize(question)
    if not query_terms:
        return chunks[:limit]

    scored_chunks = []
    for chunk in chunks:
        chunk_terms = _tokenize(chunk)
        overlap = query_terms.intersection(chunk_terms)
        scored_chunks.append((len(overlap), chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _score, chunk in scored_chunks[:limit]]


def _answer_with_model(relevant_chunks: list[str], question: str) -> str:
    context = "\n\n".join(relevant_chunks)
    model = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.answer_model,
        temperature=0,
    )
    response = model.invoke(
        [
            (
                "system",
                "You answer questions about a single medical record. Use only the provided context. "
                "If the answer is not present, say that the record does not contain it.",
            ),
            (
                "human",
                f"Context:\n{context}\n\nQuestion: {question}",
            ),
        ]
    )
    return response.content if isinstance(response.content, str) else str(response.content)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(left_value * right_value for left_value, right_value in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)
