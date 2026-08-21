from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionService
)
from app.services.extractors.invoice_extractor import (
    InvoiceExtractor
)


BASE_DIR = Path(__file__).resolve().parent.parent


def test_invoice(relative_path):

    file_path = BASE_DIR / relative_path

    text_service = TextExtractionService()
    extractor = InvoiceExtractor()

    extraction_result = text_service.extract(
        file_path
    )

    invoice = extractor.extract(
        extraction_result["text"]
    )

    print("\n" + "=" * 70)

    print("FILE:", file_path.name)

    print("\nSTRUCTURED INVOICE:\n")

    print(
        invoice.model_dump_json(
            indent=2
        )
    )


def main():

    test_invoice(
        "sample_data/invoices/invoice_standard.pdf"
    )

    test_invoice(
        "sample_data/invoices/invoice_modern.pdf"
    )

    test_invoice(
        "sample_data/invoices/invoice_scanned.png"
    )


if __name__ == "__main__":
    main()