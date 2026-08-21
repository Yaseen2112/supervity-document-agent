from pathlib import Path

from app.services.text_extraction_service import (
    TextExtractionService
)


BASE_DIR = Path(__file__).resolve().parent.parent

file_path = (
    BASE_DIR
    / "sample_data/invoices/invoice_modern.pdf"
)

text_service = TextExtractionService()

result = text_service.extract(file_path)

print("\n" + "=" * 70)
print("EXTRACTED TEXT")
print("=" * 70)

print(result["text"])