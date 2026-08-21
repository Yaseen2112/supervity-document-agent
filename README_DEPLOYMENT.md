# 📄 Document Extraction & Structuring Agent

A lightweight, robust document processing agent that classifies vendor documents (invoices, delivery notes, contracts) and converts them into structured JSON using rule-based extraction and OCR.

## ✨ Key Features

- **Multi-Format Support**: PDF (text & scanned), PNG, JPG, JPEG
- **Document Classification**: Automatically identifies document type
- **OCR Capability**: Extracts text from scanned documents with confidence scoring
- **Structured Extraction**: Converts document data into validated JSON schemas
- **Quality Detection**: Flags low-quality documents for manual review
- **No LLM Dependency**: Fast, deterministic, offline processing
- **Production Ready**: Fully tested with comprehensive sample documents

## 📊 Supported Document Types

### 1. **Invoice**
Extracts: Invoice number, dates, vendor info, line items, amounts, tax, currency

### 2. **Delivery Note**
Extracts: Delivery note number, vendor, recipient, delivery date, items, status

### 3. **Contract**
Extracts: Contract ID, title, parties, dates, payment terms, key obligations, termination clauses

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/supervity-document-agent.git
cd supervity-document-agent

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run comprehensive test suite
python run_tests.py

# Run specific model tests
python -m pytest tests/test_models.py -v

# Test specific document type
python -c "
from app.services.document_orchestrator import DocumentOrchestrator
orchestrator = DocumentOrchestrator()
result = orchestrator.process('sample_data/invoices/invoice_standard.pdf')
import json
print(json.dumps(result, indent=2))
"
```

### Using the Streamlit App

```bash
streamlit run streamlit_app.py
```

Then open `http://localhost:8501` in your browser and upload documents.

## 📁 Project Structure

```
supervity-document-agent/
├── app/
│   ├── models/              # Pydantic data models
│   │   ├── invoice.py
│   │   ├── delivery_note.py
│   │   ├── contract.py
│   │   └── response.py
│   ├── services/            # Core extraction services
│   │   ├── classifier.py
│   │   ├── document_orchestrator.py
│   │   ├── text_extraction_service.py
│   │   ├── ocr_service.py
│   │   ├── ocr_correction_service.py
│   │   └── extractors/
│   │       ├── invoice_extractor.py
│   │       ├── delivery_note_extractor.py
│   │       └── contract_extractor.py
│   └── utils/               # Utility functions
├── sample_data/             # Sample test documents
│   ├── invoices/
│   ├── delivery_notes/
│   ├── contracts/
│   └── low_quality/
├── tests/                   # Test suite
│   ├── test_models.py
│   ├── test_document_orchestrator.py
│   ├── test_invoice_extractor.py
│   ├── test_delivery_note_extractor.py
│   ├── test_contract_extractor.py
│   └── ...
├── streamlit_app.py         # Web interface
├── run_tests.py             # Comprehensive test runner
└── requirements.txt         # Python dependencies
```

## 🔄 Processing Pipeline

```
PDF / Image Input
       ↓
Text Extraction / OCR
       ↓
Document Classification
       ↓
Document-Specific Extraction
       ↓
Pydantic Model Validation
       ↓
JSON Output
```

## 📊 Test Results

- ✅ **8 Sample Documents Tested**: 100% Success Rate
- ✅ **4 Model Types Tested**: All JSON serialization working
- ✅ **OCR Handling Verified**: Low-quality document detection
- ✅ **13 Total Tests**: All passing

### Sample Test Coverage

| Document | Type | Status | Confidence |
|----------|------|--------|------------|
| invoice_standard.pdf | Invoice | ✅ | 100% |
| invoice_modern.pdf | Invoice | ✅ | 97% |
| invoice_scanned.png | Invoice (OCR) | ✅ | 93.25% |
| delivery_note_standard.pdf | Delivery Note | ✅ | 92% |
| delivery_note_landscape.pdf | Delivery Note | ✅ | 89% |
| contract_simple.pdf | Contract | ✅ | 90% |
| contract_standard.pdf | Contract | ✅ | 90% |
| contract_unusual.pdf | Contract | ✅ | 69% |

## 💡 API Usage

### Python

```python
from app.services.document_orchestrator import DocumentOrchestrator
import json

orchestrator = DocumentOrchestrator()

# Process a document
result = orchestrator.process('path/to/invoice.pdf')

# Get structured data
invoice_data = result['data']
confidence = result['classification']['confidence']
requires_review = result['metadata']['requires_review']

# Serialize to JSON
json_output = json.dumps(result, indent=2)
```

### Expected JSON Output

```json
{
  "metadata": {
    "filename": "invoice.pdf",
    "file_type": "pdf",
    "page_count": 1,
    "extraction_method": "embedded_text",
    "ocr_confidence": null,
    "requires_review": false
  },
  "classification": {
    "document_type": "invoice",
    "confidence": 1.0,
    "matched_keywords": ["invoice", "total amount", "tax"],
    "scores": {
      "invoice": 19.0,
      "delivery_note": 0.0,
      "contract": 0.0
    }
  },
  "data": {
    "document_type": "invoice",
    "invoice_number": "INV-2026-001",
    "invoice_date": "2026-08-21",
    "due_date": "2026-09-20",
    "vendor": {
      "name": "TechSupply Solutions",
      "address": "Hyderabad, India"
    },
    "line_items": [
      {
        "description": "Laptop",
        "quantity": 2,
        "unit_price": 50000,
        "total": 100000
      }
    ],
    "subtotal": 100000,
    "tax": 18000,
    "total_amount": 118000
  }
}
```

## 🎯 Quality Metrics

### Classification Confidence
- **≥ 90%**: Excellent - Direct extraction recommended
- **70-89%**: Good - Minor review may be needed
- **50-69%**: Fair - Review recommended
- **< 50%**: Poor - Manual extraction recommended

### OCR Quality Flags
- `ocr_confidence`: Percentage confidence in OCR extraction (0-100)
- `requires_review`: Boolean flag for low-quality documents
- Set to `true` when OCR confidence < 85%

## 🛠️ Technologies Used

- **Python 3.10+**
- **Pydantic**: Data validation
- **PyMuPDF**: PDF processing
- **Pytesseract**: OCR
- **Streamlit**: Web UI
- **Pillow**: Image processing
- **OpenCV**: Image preprocessing

## 📝 Environment Setup

Create a `.env` file for optional configuration:

```env
TESSERACT_PATH=/usr/bin/tesseract  # Path to Tesseract binary (Linux/Mac)
# Windows uses registry path automatically
MIN_OCR_CONFIDENCE=85
```

## 🐛 Troubleshooting

### OCR not working on Windows
- Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add installation path to PATH environment variable or .env file

### Memory issues with large PDFs
- Process documents in batches
- Reduce image preprocessing quality if needed

### Low extraction confidence
- Check document quality (scans should be 300+ DPI)
- Verify document layout is standard
- Check `requires_review` flag in metadata

## 📚 Documentation

- See `README.md` for full documentation
- See `app/services/` for service documentation
- See `app/models/` for Pydantic schema definitions
- See `tests/` for usage examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

[Add your license here]

## 👤 Author

Created for Supervity Document Processing

## 🔗 Links

- **GitHub**: [Repository URL]
- **Documentation**: [Docs URL]
- **Issues**: [Issues URL]

---

**Last Updated**: 2026-08-21
**Version**: 1.0.0
**Status**: Production Ready ✅
