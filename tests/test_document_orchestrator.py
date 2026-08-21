from pathlib import Path
import json

from app.services.document_orchestrator import (
    DocumentOrchestrator
)


BASE_DIR = (
    Path(__file__).resolve().parent.parent
)


def test_document(
    relative_path: str,
    orchestrator: DocumentOrchestrator
):

    file_path = (
        BASE_DIR / relative_path
    )

    print("\n" + "=" * 80)

    print(
        "PROCESSING:",
        file_path.name
    )

    try:

        result = orchestrator.process(
            file_path
        )

        print(
            json.dumps(
                result,
                indent=2
            )
        )

    except Exception as error:

        print(
            "ERROR:",
            str(error)
        )


def main():

    orchestrator = (
        DocumentOrchestrator()
    )

    # ----------------------------------
    # INVOICES
    # ----------------------------------

    test_document(
        "sample_data/invoices/invoice_standard.pdf",
        orchestrator
    )

    test_document(
        "sample_data/invoices/invoice_modern.pdf",
        orchestrator
    )

    test_document(
        "sample_data/invoices/invoice_scanned.png",
        orchestrator
    )

    # ----------------------------------
    # DELIVERY NOTES
    # ----------------------------------

    test_document(
        "sample_data/delivery_notes/"
        "delivery_note_standard.pdf",
        orchestrator
    )

    test_document(
        "sample_data/delivery_notes/"
        "delivery_note_landscape.pdf",
        orchestrator
    )

    # ----------------------------------
    # CONTRACTS
    # ----------------------------------

    test_document(
        "sample_data/contracts/contract_simple.pdf",
        orchestrator
    )

    test_document(
        "sample_data/contracts/contract_standard.pdf",
        orchestrator
    )

    test_document(
        "sample_data/contracts/contract_unusual.pdf",
        orchestrator
    )


if __name__ == "__main__":
    main()