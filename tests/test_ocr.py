from pathlib import Path

from app.services.document_processor import DocumentProcessor
from app.services.image_preprocessor import ImagePreprocessor
from app.services.ocr_service import OCRService


BASE_DIR = Path(__file__).resolve().parent.parent


def run_ocr_test(relative_path):

    file_path = BASE_DIR / relative_path

    processor = DocumentProcessor()
    preprocessor = ImagePreprocessor()
    ocr_service = OCRService()

    document = processor.process_document(file_path)

    processed_images = []

    for image in document["images"]:

        processed_image = preprocessor.preprocess(image)

        processed_images.append(processed_image)

    result = ocr_service.extract_text_from_images(
        processed_images
    )

    print("\n" + "=" * 60)

    print(f"FILE: {file_path.name}")

    print("=" * 60)

    print(
        "\nOCR CONFIDENCE:",
        result["average_confidence"]
    )

    print("\nEXTRACTED TEXT:\n")

    print(result["text"])


def main():

    run_ocr_test(
        "sample_data/invoices/invoice_scanned.png"
    )

    run_ocr_test(
        "sample_data/low_quality/invoice_low_quality.png"
    )


if __name__ == "__main__":
    main()