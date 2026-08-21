from pathlib import Path

from app.services.document_processor import DocumentProcessor


BASE_DIR = Path(__file__).resolve().parent.parent


def test_standard_pdf():

    processor = DocumentProcessor()

    file_path = (
        BASE_DIR
        / "sample_data"
        / "invoices"
        / "invoice_standard.pdf"
    )

    result = processor.process_document(file_path)

    print("\n--- STANDARD PDF ---")

    print("Filename:", result["filename"])
    print("File Type:", result["file_type"])
    print("Page Count:", result["page_count"])
    print("Requires OCR:", result["requires_ocr"])

    print("\nExtracted Text:\n")
    print(result["text"])


def test_scanned_image():

    processor = DocumentProcessor()

    file_path = (
        BASE_DIR
        / "sample_data"
        / "invoices"
        / "invoice_scanned.png"
    )

    result = processor.process_document(file_path)

    print("\n--- SCANNED IMAGE ---")

    print("Filename:", result["filename"])
    print("File Type:", result["file_type"])
    print("Page Count:", result["page_count"])
    print("Requires OCR:", result["requires_ocr"])
    print("Images Loaded:", len(result["images"]))


def test_low_quality_image():

    processor = DocumentProcessor()

    file_path = (
        BASE_DIR
        / "sample_data"
        / "low_quality"
        / "invoice_low_quality.png"
    )

    result = processor.process_document(file_path)

    print("\n--- LOW QUALITY IMAGE ---")

    print("Filename:", result["filename"])
    print("File Type:", result["file_type"])
    print("Requires OCR:", result["requires_ocr"])
    print("Images Loaded:", len(result["images"]))


if __name__ == "__main__":

    test_standard_pdf()
    test_scanned_image()
    test_low_quality_image()