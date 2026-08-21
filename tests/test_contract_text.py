from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionService
)


BASE_DIR = Path(__file__).resolve().parent.parent


def test_document(relative_path):

    file_path = BASE_DIR / relative_path

    text_service = TextExtractionService()

    result = text_service.extract(
        file_path
    )

    print("\n" + "=" * 70)

    print(
        "FILE:",
        file_path.name
    )

    print("\nEXTRACTED TEXT\n")

    print(
        result["text"]
    )


def main():

    test_document(
        "sample_data/contracts/contract_simple.pdf"
    )

    test_document(
        "sample_data/contracts/contract_standard.pdf"
    )

    test_document(
        "sample_data/contracts/contract_unusual.pdf"
    )


if __name__ == "__main__":
    main()