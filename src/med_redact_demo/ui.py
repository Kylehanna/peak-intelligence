import streamlit as st
from pathlib import Path

from med_redact_demo.qa import answer_question
from med_redact_demo.redaction import redact_pdf


st.set_page_config(page_title="Peak Intelligence", layout="wide")


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLE_PDF_PATH = PROJECT_ROOT / "sample_data" / "deidentified_medical_record.pdf"
SOURCE_SAMPLE_PDF_PATH = PROJECT_ROOT / "sample_data" / "synthetic_medical_record_source.pdf"


def main() -> None:
    st.title("Peak Intelligence")
    st.caption("AI-assisted document redaction and question answering for privacy-sensitive legal workflows.")
    st.info("Run this prototype locally with synthetic records only. No persistent storage is built into the app.")
    st.sidebar.header("Demo prompts")
    st.sidebar.write("Try these after redaction:")
    st.sidebar.write("- What medications were prescribed?")
    st.sidebar.write("- Summarize the recent visit.")
    st.sidebar.write("- What follow-up was recommended?")
    st.sidebar.write("- What diagnostics were ordered?")

    source_bytes: bytes | None = None
    source_name: str | None = None

    if DEFAULT_SAMPLE_PDF_PATH.exists() and "active_source_bytes" not in st.session_state:
        st.session_state["active_source_bytes"] = DEFAULT_SAMPLE_PDF_PATH.read_bytes()
        st.session_state["active_source_name"] = DEFAULT_SAMPLE_PDF_PATH.name

    if DEFAULT_SAMPLE_PDF_PATH.exists() and st.button("Use bundled de-identified sample"):
        source_bytes = DEFAULT_SAMPLE_PDF_PATH.read_bytes()
        source_name = DEFAULT_SAMPLE_PDF_PATH.name
        st.session_state["active_source_bytes"] = source_bytes
        st.session_state["active_source_name"] = source_name

    if SOURCE_SAMPLE_PDF_PATH.exists() and st.button("Use bundled source sample"):
        source_bytes = SOURCE_SAMPLE_PDF_PATH.read_bytes()
        source_name = SOURCE_SAMPLE_PDF_PATH.name
        st.session_state["active_source_bytes"] = source_bytes
        st.session_state["active_source_name"] = source_name

    uploaded_file = st.file_uploader("Medical record PDF", type=["pdf"])
    if uploaded_file is not None:
        source_bytes = uploaded_file.getvalue()
        source_name = uploaded_file.name
        st.session_state["active_source_bytes"] = source_bytes
        st.session_state["active_source_name"] = source_name

    if source_bytes is None:
        source_bytes = st.session_state.get("active_source_bytes")
        source_name = st.session_state.get("active_source_name")

    if not source_bytes:
        st.info("A bundled de-identified sample should load automatically. You can also upload a PDF or switch samples.")
        return

    st.caption(f"Active document: {source_name}")

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Redaction")
        if st.button("Redact PDF", type="primary"):
            result = redact_pdf(source_bytes)
            st.session_state["redaction_result"] = result

        result = st.session_state.get("redaction_result")
        if result:
            st.success(f"Redacted {result.entity_count} candidate entities.")
            for warning in result.warnings:
                st.warning(warning)
            st.download_button(
                "Download redacted PDF",
                data=result.redacted_pdf_bytes,
                file_name="redacted_record.pdf",
                mime="application/pdf",
            )
            with st.expander("Redacted text preview", expanded=False):
                st.text(result.redacted_text[:4000] or "No text extracted.")

    with right:
        st.subheader("Ask questions")
        question = st.text_input("Question", placeholder="What medications were prescribed?")
        if st.button("Ask"):
            result = st.session_state.get("redaction_result")
            if not result:
                st.info("Redact a PDF first.")
            elif not question.strip():
                st.info("Enter a question.")
            else:
                answer = answer_question(result.redacted_text, question)
                st.write(answer)
