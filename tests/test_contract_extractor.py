from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionService
)

from app.services.extractors.contract_extractor import (
    ContractExtractor
)


BASE_DIR = Path(__file__).resolve().parent.parent


def test_contract(relative_path):

    file_path = BASE_DIR / relative_path

    text_service = TextExtractionService()

    extractor = ContractExtractor()

    extraction_result = text_service.extract(
        file_path
    )

    contract = extractor.extract(
        extraction_result["text"]
    )

    print("\n" + "=" * 70)

    print(
        "FILE:",
        file_path.name
    )

    print("\nSTRUCTURED CONTRACT:\n")

    print(
        contract.model_dump_json(
            indent=2
        )
    )


def main():

    test_contract(
        "sample_data/contracts/contract_simple.pdf"
    )

    test_contract(
        "sample_data/contracts/contract_standard.pdf"
    )

    test_contract(
        "sample_data/contracts/contract_unusual.pdf"
    )


if __name__ == "__main__":
    main()