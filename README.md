# Peak Intelligence

Peak Intelligence is a lightweight AI document-intelligence platform prototype built to show how legal and professional-services teams can upload sensitive records, redact likely PII, and query the sanitized output in a controlled local workflow.

This repository is positioned as:
- A first AI solution for law firm client conversations
- A working proof-of-build for recruiters evaluating product, applied AI, and workflow automation experience
- An early platform foundation for broader document review, privacy, and knowledge-extraction use cases

## Platform Positioning

Peak Intelligence is not framed as a one-off script. It is framed as the beginning of a platform: intake, detection, redaction, safe handoff, and question answering over cleaned documents.

The current implementation focuses on one clear workflow:
- upload a medical or case-adjacent PDF
- detect likely sensitive information
- apply redactions
- download a sanitized file
- ask questions against the redacted text

That workflow is narrow by design, but it demonstrates the core product pattern behind a larger legal AI platform.

## Why This Matters

Law firms routinely handle intake packets, medical records, discovery materials, expert documents, and client records that require both speed and care. Peak Intelligence shows how AI can support that work without pretending to replace legal judgment.

The immediate value is operational:
- faster first-pass redaction
- cleaner documents for internal review or external sharing
- faster document understanding through Q&A on sanitized text
- a more repeatable intake and review workflow for high-volume matters

## Core Use Cases

Peak Intelligence is currently best suited for early-stage use cases such as:
- medical record review for personal injury, workers compensation, disability, and malpractice matters
- pre-production redaction support before sending records to experts, clients, or opposing counsel
- internal legal ops demos showing how AI can reduce manual document triage
- privacy-first AI workflow demonstrations for law firm innovation teams
- recruiter-facing portfolio proof for AI product, legal tech, and applied data roles

## Current Product Scope

The current app supports:
- PDF upload
- candidate PII detection
- redacted PDF download
- redacted-text preview
- question answering against the redacted text

This is intentionally version-one scope. It is designed to demonstrate the product loop clearly rather than cover every entity type or legal workflow on day one.

## Product Narrative For Demos

When presenting this repository, the strongest framing is:

Peak Intelligence is an early legal-document intelligence platform that starts with privacy-sensitive document intake. The first implemented workflow is medical PDF redaction and AI-assisted review, which is directly relevant for law firm clients handling regulated or confidential records.

For recruiters, this repo shows end-to-end product thinking:
- user-facing interface design
- document processing and text extraction
- PII detection and redaction logic
- retrieval-style Q&A workflow
- local-first privacy-aware architecture

## Architecture

The current stack is:
- Streamlit for the application UI
- PyMuPDF for PDF parsing and redaction overlays
- Microsoft Presidio for entity detection when spaCy models are available
- regex fallback rules for core identifiers and contact data
- LangChain plus OpenAI models for text chunking and Q&A

## Setup

1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies with `pip install -e .`.
3. Install a spaCy English model for Presidio:
   `python -m spacy download en_core_web_sm`
4. Set `OPENAI_API_KEY` in your environment for model-backed Q&A.
5. Start the app with `streamlit run app.py`.

## Demo Inputs

Generate bundled synthetic demo records with:

`./.venv/bin/python scripts/generate_sample_pdf.py`

This produces:
- `sample_data/deidentified_medical_record.pdf` for the default demo flow
- `sample_data/synthetic_medical_record_source.pdf` for source redaction testing

The app loads the de-identified sample automatically on first run. You can also switch between bundled inputs or upload your own synthetic PDF.

Suggested demo prompts:
- What medications were prescribed?
- Summarize the recent visit.
- What follow-up was recommended?
- What diagnostics were ordered?
- What information appears to have been redacted?

## Roadmap Direction

The natural next steps for the platform are:
- stronger organization and facility-name detection
- better address and identifier coverage
- matter-specific redaction presets for legal workflows
- audit logging and review controls
- support for broader legal document classes beyond medical records

## Guardrails

- Use synthetic records only for demos.
- Keep the workflow local unless governance and security requirements are clearly addressed.
- Treat the redaction output as assistive, not final legal review.
- If no OpenAI key is configured, the app can still provide excerpt-based responses from the redacted document.
