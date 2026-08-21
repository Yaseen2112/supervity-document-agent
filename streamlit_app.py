import json
import tempfile
from pathlib import Path

import streamlit as st

from app.services.document_orchestrator import DocumentOrchestrator


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Document Extraction Agent",
    page_icon="📄",
    layout="wide"
)


# ---------------------------------------------------------
# INITIALIZE SERVICES
# ---------------------------------------------------------

orchestrator = DocumentOrchestrator()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("📄 Document Extraction & Structuring Agent")

st.write(
    "Upload an invoice, delivery note, or contract "
    "in PDF, PNG, JPG, or JPEG format."
)

st.caption(
    "Pipeline: Document → Text/OCR → Classification → "
    "Structured Extraction → Confidence / Review"
)


# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Document",
    type=["pdf", "png", "jpg", "jpeg"]
)


# ---------------------------------------------------------
# PROCESS DOCUMENT
# ---------------------------------------------------------

if uploaded_file is not None:

    st.divider()

    # Create temporary file
    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(
            uploaded_file.getbuffer()
        )

        temp_path = temp_file.name

    try:

        # -------------------------------------------------
        # 1. TEXT EXTRACTION
        # -------------------------------------------------

        with st.spinner("Extracting document text..."):

            pipeline_result = orchestrator.process(
                temp_path
            )

        metadata = pipeline_result["metadata"]
        classification = pipeline_result["classification"]
        structured_data = pipeline_result["data"]
        document_type = classification["document_type"]
        confidence = classification["confidence"]

        # -------------------------------------------------
        # 3. DISPLAY DOCUMENT INFORMATION
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Document Type",
                document_type.upper()
            )

        with col2:
            st.metric(
                "Classification Confidence",
                f"{confidence * 100:.1f}%"
            )

        with col3:

            if metadata["requires_review"]:
                st.warning("⚠️ Review Required")
            else:
                st.success("✅ No Review Required")

        # -------------------------------------------------
        # 4. EXTRACTION METADATA
        # -------------------------------------------------

        st.subheader("Extraction Information")

        metadata = {
            "filename": uploaded_file.name,
            "file_type": metadata["file_type"],
            "page_count": metadata["page_count"],
            "extraction_method": metadata["extraction_method"],
            "ocr_confidence": metadata["ocr_confidence"],
            "requires_review": metadata["requires_review"]
        }

        st.json(metadata)

        # -------------------------------------------------
        # 5. CLASSIFICATION DETAILS
        # -------------------------------------------------

        st.subheader("Classification")

        st.json(classification)

        # -------------------------------------------------
        # 7. DISPLAY STRUCTURED JSON
        # -------------------------------------------------

        st.subheader("Structured JSON")

        st.json(
            structured_data
        )

        # -------------------------------------------------
        # DOWNLOAD JSON
        # -------------------------------------------------

        json_data = json.dumps(
            structured_data,
            indent=2,
            ensure_ascii=False
        )

        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name=(
                Path(uploaded_file.name).stem
                + ".json"
            ),
            mime="application/json"
        )

        # -------------------------------------------------
        # 8. EXTRACTED TEXT
        # -------------------------------------------------

        with st.expander(
            "View Extracted Text"
        ):

            st.text_area(
                "Text",
                pipeline_result.get("text", ""),
                height=300
            )

    except Exception as e:

        st.error(
            "Document processing failed."
        )

        st.exception(e)

    finally:

        # Remove temporary file
        try:
            Path(temp_path).unlink(
                missing_ok=True
            )
        except Exception:
            pass