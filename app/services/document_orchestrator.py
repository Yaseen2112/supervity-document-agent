from pathlib import Path
from typing import Dict, Any

from app.services.text_extraction_service import (
    TextExtractionService
)

from app.services.classifier import (
    DocumentClassifier
)

from app.services.ocr_correction_service import (
    OCRCorrectionService
)

from app.services.extractors.invoice_extractor import (
    InvoiceExtractor
)

from app.services.extractors.delivery_note_extractor import (
    DeliveryNoteExtractor
)

from app.services.extractors.contract_extractor import (
    ContractExtractor
)


class UnsupportedDocumentError(Exception):
    """
    Raised when the document type cannot be identified.
    """

    pass


class DocumentOrchestrator:

    def __init__(self):

        self.text_extraction_service = (
            TextExtractionService()
        )

        self.document_classifier = (
            DocumentClassifier()
        )

        self.ocr_correction_service = (
            OCRCorrectionService()
        )

        self.invoice_extractor = (
            InvoiceExtractor()
        )

        self.delivery_note_extractor = (
            DeliveryNoteExtractor()
        )

        self.contract_extractor = (
            ContractExtractor()
        )

    def extract_structured_data(
        self,
        text: str,
        document_type: str
    ):
        """
        Route the extracted text to the
        correct document-specific extractor.
        """

        if document_type == "invoice":

            return self.invoice_extractor.extract(
                text
            )

        if document_type == "delivery_note":

            return self.delivery_note_extractor.extract(
                text
            )

        if document_type == "contract":

            return self.contract_extractor.extract(
                text
            )

        raise UnsupportedDocumentError(
            f"Unsupported document type: "
            f"{document_type}"
        )

    def process(
        self,
        file_path: str | Path
    ) -> Dict[str, Any]:
        """
        Complete document processing pipeline.

        Steps:
        1. Extract text.
        2. Classify document.
        3. Route to correct extractor.
        4. Return structured result.
        """

        # ----------------------------------
        # STEP 1: TEXT EXTRACTION
        # ----------------------------------

        extraction_result = (
            self.text_extraction_service.extract(
                file_path
            )
        )

        text = self.ocr_correction_service.correct_common_ocr_errors(
            extraction_result["text"]
        )

        # ----------------------------------
        # STEP 2: DOCUMENT CLASSIFICATION
        # ----------------------------------

        classification_result = (
            self.document_classifier.classify(
                text
            )
        )

        document_type = (
            classification_result["document_type"]
        )

        # ----------------------------------
        # STEP 3: UNKNOWN DOCUMENT CHECK
        # ----------------------------------

        if document_type == "unknown":

            raise UnsupportedDocumentError(
                "Unable to identify document type."
            )

        # ----------------------------------
        # STEP 4: STRUCTURED EXTRACTION
        # ----------------------------------

        structured_data = (
            self.extract_structured_data(
                text=text,
                document_type=document_type
            )
        )

        # ----------------------------------
        # STEP 5: FINAL RESPONSE
        # ----------------------------------

        return {
            "text": text,
            "metadata": {
                "filename": extraction_result[
                    "filename"
                ],
                "file_type": extraction_result[
                    "file_type"
                ],
                "page_count": extraction_result[
                    "page_count"
                ],
                "extraction_method": extraction_result[
                    "extraction_method"
                ],
                "ocr_confidence": extraction_result[
                    "ocr_confidence"
                ],
                "requires_review": extraction_result[
                    "requires_review"
                ]
            },

            "classification": {
                "document_type": document_type,
                "confidence": classification_result[
                    "confidence"
                ],
                "matched_keywords": classification_result[
                    "matched_keywords"
                ],
                "scores": classification_result[
                    "scores"
                ]
            },

            "data": structured_data.model_dump()
        }