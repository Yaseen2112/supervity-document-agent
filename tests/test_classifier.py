from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionService
)

from app.services.classifier import (
    DocumentClassifier
)


BASE_DIR = Path(__file__).resolve().parent.parent


def test_document(relative_path):

    file_path = BASE_DIR / relative_path

    extraction_service = TextExtractionService()

    classifier = DocumentClassifier()

    extraction_result = extraction_service.extract(
        file_path
    )

    classification = classifier.classify(
        extraction_result["text"]
    )

    print("\n" + "=" * 70)

    print("FILE:", file_path.name)

    print(
        "DOCUMENT TYPE:",
        classification["document_type"]
    )

    print(
        "CONFIDENCE:",
        classification["confidence"]
    )

    print(
        "MATCHED KEYWORDS:",
        classification["matched_keywords"]
    )

    print(
        "ALL SCORES:",
        classification["scores"]
    )


def main():

    # Invoices
    test_document(
        "sample_data/invoices/invoice_standard.pdf"
    )

    test_document(
        "sample_data/invoices/invoice_modern.pdf"
    )

    test_document(
        "sample_data/invoices/invoice_scanned.png"
    )

    # Delivery Notes
    test_document(
        "sample_data/delivery_notes/delivery_note_standard.pdf"
    )

    test_document(
        "sample_data/delivery_notes/delivery_note_landscape.pdf"
    )

    # Contracts
    test_document(
        "sample_data/contracts/contract_standard.pdf"
    )

    test_document(
        "sample_data/contracts/contract_simple.pdf"
    )

    test_document(
        "sample_data/contracts/contract_unusual.pdf"
    )

    # Low-quality document
    test_document(
        "sample_data/low_quality/invoice_low_quality.png"
    )


if __name__ == "__main__":
    main()