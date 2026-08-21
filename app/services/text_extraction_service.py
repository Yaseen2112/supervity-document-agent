from pathlib import Path
from typing import Dict, Any

from app.services.document_processor import DocumentProcessor
from app.services.image_preprocessor import ImagePreprocessor
from app.services.ocr_service import OCRService


class TextExtractionService:

    def __init__(self):

        self.document_processor = DocumentProcessor()

        self.image_preprocessor = ImagePreprocessor()

        self.ocr_service = OCRService()

    def extract(
        self,
        file_path: str | Path
    ) -> Dict[str, Any]:
        """
        Extract text from a PDF or image.

        Strategy:
        1. Use embedded PDF text when available.
        2. Fall back to OCR for scanned PDFs.
        3. Use OCR for image files.
        """

        document = self.document_processor.process_document(
            file_path
        )

        # ---------------------------------
        # CASE 1: PDF WITH EMBEDDED TEXT
        # ---------------------------------

        if (
            document["file_type"] == "pdf"
            and not document["requires_ocr"]
        ):

            return {
                "filename": document["filename"],
                "file_type": document["file_type"],
                "page_count": document["page_count"],
                "extraction_method": "embedded_text",
                "text": document["text"],
                "ocr_confidence": None,
                "requires_review": False
            }

        # ---------------------------------
        # CASE 2: IMAGE OR SCANNED PDF
        # ---------------------------------

        processed_images = []

        for image in document["images"]:

            processed_image = (
                self.image_preprocessor.preprocess(image)
            )

            processed_images.append(
                processed_image
            )

        ocr_result = (
            self.ocr_service.extract_text_from_images(
                processed_images
            )
        )

        ocr_confidence = (
            ocr_result["average_confidence"]
        )

        # Initial OCR confidence rule
        requires_review = ocr_confidence < 60

        return {
            "filename": document["filename"],
            "file_type": document["file_type"],
            "page_count": document["page_count"],
            "extraction_method": "ocr",
            "text": ocr_result["text"],
            "ocr_confidence": ocr_confidence,
            "requires_review": requires_review
        }