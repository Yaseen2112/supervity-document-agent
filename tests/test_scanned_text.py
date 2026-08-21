from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionService
)


BASE_DIR = Path(__file__).resolve().parent.parent


def main():

    file_path = (
        BASE_DIR
        / "sample_data/invoices/invoice_scanned.png"
    )

    text_service = TextExtractionService()

    extraction_result = text_service.extract(
        file_path
    )

    print("\n" + "=" * 70)

    print("FILE:", file_path.name)

    print("\nEXTRACTED TEXT\n")

    print(
        extraction_result["text"]
    )


if __name__ == "__main__":
    main()