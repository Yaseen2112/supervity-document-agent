from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionService
)


BASE_DIR = Path(__file__).resolve().parent.parent


def test_document(relative_path):

    file_path = BASE_DIR / relative_path

    service = TextExtractionService()

    result = service.extract(file_path)

    print("\n" + "=" * 70)

    print("FILE:", result["filename"])

    print("FILE TYPE:", result["file_type"])

    print(
        "EXTRACTION METHOD:",
        result["extraction_method"]
    )

    print(
        "OCR CONFIDENCE:",
        result["ocr_confidence"]
    )

    print(
        "REQUIRES REVIEW:",
        result["requires_review"]
    )

    print("\nEXTRACTED TEXT:\n")

    print(result["text"])


def main():

    test_document(
        "sample_data/invoices/invoice_standard.pdf"
    )

    test_document(
        "sample_data/invoices/invoice_scanned.png"
    )

    test_document(
        "sample_data/low_quality/invoice_low_quality.png"
    )


if __name__ == "__main__":
    main()