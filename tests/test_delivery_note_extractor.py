from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionService
)

from app.services.extractors.delivery_note_extractor import (
    DeliveryNoteExtractor
)


BASE_DIR = Path(__file__).resolve().parent.parent


def test_delivery_note(relative_path):

    file_path = BASE_DIR / relative_path

    text_service = TextExtractionService()

    extractor = DeliveryNoteExtractor()

    extraction_result = text_service.extract(
        file_path
    )

    delivery_note = extractor.extract(
        extraction_result["text"]
    )

    print("\n" + "=" * 70)

    print(
        "FILE:",
        file_path.name
    )

    print("\nSTRUCTURED DELIVERY NOTE:\n")

    print(
        delivery_note.model_dump_json(
            indent=2
        )
    )


def main():

    test_delivery_note(
        "sample_data/delivery_notes/delivery_note_standard.pdf"
    )

    test_delivery_note(
        "sample_data/delivery_notes/delivery_note_landscape.pdf"
    )


if __name__ == "__main__":
    main()