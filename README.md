# 📄 Document Extraction & Structuring Agent

A lightweight document processing agent that classifies vendor documents and converts them into structured JSON.

This project is designed for **Problem 6: Document Extraction & Structuring Agent**, where the input consists of differently formatted **invoices, delivery notes, and contracts** provided as PDFs or images.

The system focuses on **document format variation, OCR handling, schema-based extraction, confidence scoring, and review detection** without relying on LLMs or external AI services.

---

## 🎯 Problem Statement

Given a folder of differently formatted vendor documents such as:

* Invoices
* Delivery Notes
* Contracts

in formats such as:

* PDF
* PNG
* JPG
* JPEG

the system must:

1. Classify each document into its correct type.
2. Extract relevant information.
3. Return a structured JSON representation.
4. Handle unusually formatted or scanned documents.
5. Report confidence and identify documents requiring review.

---

## ✨ Key Features

* 📄 PDF document support
* 🖼️ PNG, JPG, and JPEG image support
* 🔍 Embedded PDF text extraction
* 👁️ OCR for scanned PDFs and images
* 🧹 Image preprocessing for improved OCR quality
* 🏷️ Rule-based document classification
* 🧾 Invoice extraction
* 📦 Delivery note extraction
* 📑 Contract extraction
* 📐 Pydantic-based structured schemas
* 📊 Classification confidence scoring
* 🔍 Classification evidence reporting
* ⚠️ OCR confidence scoring
* 🚩 Automatic review flag for low-confidence extraction
* 🔄 Robustness against document layout and terminology variations
* 📥 JSON download from the Streamlit interface
* 🌐 Interactive Streamlit UI
* 🚫 No LLM required
* 🚫 No Vector Database required
* 🚫 No external AI API required

---

# 🏗️ Architecture

```text
                         ┌────────────────────────┐
                         │      PDF / Image       │
                         │ PDF / PNG / JPG / JPEG │
                         └───────────┬────────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │  Document Processor    │
                         │                        │
                         │ • File validation      │
                         │ • PDF text extraction  │
                         │ • PDF → Image          │
                         │ • Image loading        │
                         └───────────┬────────────┘
                                     │
                         ┌───────────┴────────────┐
                         │                        │
                         ▼                        ▼
                ┌─────────────────┐      ┌─────────────────────┐
                │ Embedded Text   │      │    OCR Required     │
                │ Available       │      │                     │
                └────────┬────────┘      └──────────┬──────────┘
                         │                          │
                         │                          ▼
                         │                ┌─────────────────────┐
                         │                │ Image Preprocessor  │
                         │                │                     │
                         │                │ • Grayscale         │
                         │                │ • Upscaling         │
                         │                │ • Denoising         │
                         │                │ • CLAHE             │
                         │                │ • Thresholding      │
                         │                └──────────┬──────────┘
                         │                           │
                         │                           ▼
                         │                ┌─────────────────────┐
                         │                │     OCR Service     │
                         │                │     Tesseract       │
                         │                └──────────┬──────────┘
                         │                           │
                         └──────────────┬────────────┘
                                        │
                                        ▼
                         ┌────────────────────────┐
                         │  Document Classifier   │
                         │                        │
                         │ • Invoice              │
                         │ • Delivery Note        │
                         │ • Contract             │
                         └───────────┬────────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
                 ▼                   ▼                   ▼
        ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
        │ Invoice        │  │ Delivery Note  │  │ Contract       │
        │ Extractor      │  │ Extractor      │  │ Extractor      │
        └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
                │                   │                   │
                └───────────────────┼───────────────────┘
                                    │
                                    ▼
                         ┌────────────────────────┐
                         │   Pydantic Schemas     │
                         │                        │
                         │   Structured JSON      │
                         └───────────┬────────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │  Confidence / Review   │
                         │                        │
                         │ • Classification       │
                         │ • OCR confidence       │
                         │ • Review flag          │
                         └───────────┬────────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │     Streamlit UI       │
                         │                        │
                         │ • JSON + Metadata      │
                         │ • Extracted Text       │
                         │ • Download JSON        │
                         └────────────────────────┘
```

---

# 📁 Project Structure

```text
supervity-document-agent/
│
├── app/
│   │
│   ├── models/
│   │   ├── invoice.py
│   │   ├── delivery_note.py
│   │   ├── contract.py
│   │   └── response.py
│   │
│   ├── services/
│   │   ├── document_processor.py
│   │   ├── image_preprocessor.py
│   │   ├── ocr_service.py
│   │   ├── text_extraction_service.py
│   │   ├── classifier.py
│   │   │
│   │   └── extractors/
│   │       ├── invoice_extractor.py
│   │       ├── delivery_note_extractor.py
│   │       └── contract_extractor.py
│   │
│   └── __init__.py
│
├── sample_data/
│   │
│   ├── invoices/
│   │   ├── invoice_standard.pdf
│   │   ├── invoice_modern.pdf
│   │   └── invoice_scanned.png
│   │
│   ├── delivery_notes/
│   │   ├── delivery_note_standard.pdf
│   │   └── delivery_note_landscape.pdf
│   │
│   └── contracts/
│       ├── contract_simple.pdf
│       ├── contract_standard.pdf
│       └── contract_unusual.pdf
│
├── tests/
│   ├── test_invoice_extractor.py
│   ├── test_delivery_note_extractor.py
│   ├── test_contract_extractor.py
│   ├── test_scanned_text.py
│   └── test_document_orchestrator.py
│
├── streamlit_app.py
├── requirements.txt
└── README.md
```

---

# 🧩 Supported Document Types

## 1. 🧾 Invoice

The invoice extractor produces structured information such as invoice number, dates, vendor details, currency, line items, subtotal, tax, and total amount.

### Example

```json
{
  "document_type": "invoice",
  "invoice_number": "INV-2026-001",
  "invoice_date": "2026-08-21",
  "due_date": "2026-09-20",
  "vendor": {
    "name": "TechSupply Solutions Pvt Ltd",
    "address": "Hyderabad, India"
  },
  "customer_name": null,
  "customer_address": null,
  "currency": "INR",
  "line_items": [
    {
      "description": "Laptop",
      "quantity": 2.0,
      "unit_price": 50000.0,
      "total": 100000.0
    }
  ],
  "subtotal": 111000.0,
  "tax": 19980.0,
  "total_amount": 130980.0
}
```

---

## 2. 📦 Delivery Note

The delivery note extractor captures delivery information including document number, vendor, delivery date, recipient, delivered items, quantities, and delivery status.

### Example

```json
{
  "document_type": "delivery_note",
  "delivery_note_number": "DN-2026-001",
  "vendor_name": "TechSupply Solutions Pvt Ltd",
  "delivery_date": "2026-08-21",
  "recipient": {
    "name": "Supervity Demo Corporation",
    "address": "Bengaluru, India"
  },
  "items": [
    {
      "description": "Laptop",
      "ordered_quantity": 10.0,
      "delivered_quantity": 10.0,
      "unit": "pieces"
    }
  ],
  "delivery_status": "PARTIAL"
}
```

---

## 3. 📑 Contract

The contract extractor identifies contract metadata, parties, dates, payment terms, obligations, and termination clauses.

### Example

```json
{
  "document_type": "contract",
  "contract_id": "CTR-2026-001",
  "title": "SOFTWARE SERVICES AGREEMENT",
  "parties": [
    "TechSupply Solutions Pvt Ltd",
    "Supervity Demo Corporation"
  ],
  "effective_date": "January 1, 2026",
  "expiry_date": "December 31, 2026",
  "payment_terms": "Net 30 days from invoice date.",
  "key_obligations": [
    "TechSupply Solutions will provide agreed software services.",
    "Both parties must maintain confidentiality.",
    "Services will be delivered according to agreed milestones."
  ],
  "termination_clause": "Either party may terminate this agreement with 30 days written notice."
}
```

---

# 🔍 Document Classification

The system uses a **weighted keyword-based classifier** to determine the document type.

Each supported document type contains:

* Strong keywords
* Medium-strength keywords

Strong keywords contribute more to the classification score than medium keywords.

### Example Keyword Evidence

#### Invoice

```text
Strong:
• invoice
• invoice number
• subtotal
• tax

Medium:
• quantity
• unit price
```

#### Delivery Note

```text
Strong:
• delivery note
• delivery status
• deliver to

Medium:
• received
• supplier
```

#### Contract

```text
Strong:
• contract
• agreement
• memorandum

Medium:
• termination
• payment terms
• obligations
```

### Classification Strategy

The final classification confidence combines:

1. Relative score between the supported document types.
2. Amount of matching evidence found.

This prevents the classifier from depending on a single keyword and makes the classification process more explainable.

The system also exposes the matched keywords and classification evidence through the application.

---

# 👁️ OCR Pipeline

Scanned PDFs and image documents do not always contain machine-readable text.

The system automatically switches to OCR when embedded text is unavailable or an image document is provided.

```text
Image / Scanned PDF
        │
        ▼
Grayscale Conversion
        │
        ▼
Image Upscaling
        │
        ▼
Noise Reduction
        │
        ▼
CLAHE Contrast Enhancement
        │
        ▼
Adaptive Thresholding
        │
        ▼
Tesseract OCR
        │
        ▼
Extracted Text
```

### OCR Confidence

The OCR service calculates an average word-level confidence score.

Example:

```json
{
  "extraction_method": "ocr",
  "ocr_confidence": 93.25,
  "requires_review": false
}
```

This provides an additional signal for determining whether the extracted information should be manually reviewed.

---

# 📊 Confidence & Review Handling

The system reports confidence at two levels.

## 1. Classification Confidence

Example:

```text
Document Type: CONTRACT
Classification Confidence: 90.0%
```

This indicates how strongly the available textual evidence supports the predicted document type.

---

## 2. OCR Confidence

For scanned documents:

```text
OCR Confidence: 93.25%
Review Required: false
```

If the OCR confidence falls below the configured threshold, the system automatically sets:

```json
{
  "requires_review": true
}
```

This allows uncertain documents to be manually reviewed instead of silently accepting potentially unreliable extraction results.

---

# 🛡️ Robustness to Document Variations

The project includes multiple document layouts and terminology variations to test the extraction pipeline beyond a single happy-path template.

## Invoices

```text
invoice_standard.pdf
invoice_modern.pdf
invoice_scanned.png
```

The scanned invoice demonstrates the complete OCR-based extraction path.

---

## Delivery Notes

```text
delivery_note_standard.pdf
delivery_note_landscape.pdf
```

The landscape delivery document intentionally uses alternative terminology such as:

```text
GOODS DELIVERY RECORD
REFERENCE
SUPPLIER
DATE DELIVERED
RECEIVING COMPANY
REQUESTED
RECEIVED
```

The classifier and extractor are designed to recognize these variations while still producing the expected structured delivery-note schema.

---

## Contracts

```text
contract_simple.pdf
contract_standard.pdf
contract_unusual.pdf
```

The unusual contract deliberately uses alternative terminology such as:

```text
MEMORANDUM OF COMMERCIAL TERMS
Reference Code
Participants
becomes active
commercial arrangement concludes
Settlement condition
Exit provision
```

This tests whether the system can identify and extract contract information even when conventional terminology is replaced with equivalent wording.

---

# 🖥️ Streamlit Interface

The project includes a lightweight Streamlit interface for interactive testing and demonstration.

### Supported Upload Formats

* PDF
* PNG
* JPG
* JPEG

### The Interface Displays

* Document type
* Classification confidence
* Extraction method
* OCR confidence
* Review status
* Classification evidence
* Structured JSON
* Extracted text
* JSON download option

### Application Workflow

```text
Upload Document
      │
      ▼
Extract Text / OCR
      │
      ▼
Classify Document
      │
      ▼
Extract Structured Data
      │
      ▼
Validate with Pydantic
      │
      ▼
Calculate Confidence
      │
      ▼
Display JSON + Metadata
      │
      ▼
Download JSON
```

---

# 🚀 Installation

## 1. Clone the Repository

Replace the placeholder with your actual GitHub repository URL.

```bash
git clone https://github.com/Yaseen2112/supervity-document-agent
cd supervity-document-agent
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

Activate the environment:

```bash
source venv/bin/activate
```

---

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔧 Tesseract OCR Setup

The project uses **Tesseract OCR** for scanned documents and image-based inputs.

On Windows, install Tesseract OCR and make sure the executable path matches the configuration used in:

```text
app/services/ocr_service.py
```

Example configuration:

```python
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
```

If Tesseract is installed in a different location, update the path accordingly.

> **Note:** Tesseract must be installed separately from the Python `pytesseract` package because `pytesseract` acts as the Python integration layer for the OCR engine.

---

# ▶️ Running the Application

Start the Streamlit application with:

```bash
streamlit run streamlit_app.py
```

The application will open in your browser.

Typical local URL:

```text
http://localhost:8501
```

---

# 🧪 Running Tests

The individual document extractors can be tested directly.

### Invoice

```bash
python -m tests.test_invoice_extractor
```

### Delivery Note

```bash
python -m tests.test_delivery_note_extractor
```

### Contract

```bash
python -m tests.test_contract_extractor
```

### OCR / Scanned Documents

```bash
python -m tests.test_scanned_text
```

### Document Orchestrator

```bash
python -m tests.test_document_orchestrator
```

---

# 📋 Example Results

## Invoice

```text
Document Type: INVOICE
Confidence: 100%
Extraction: Embedded Text
Review: Not Required
```

## Scanned Invoice

```text
Document Type: INVOICE
Confidence: 100%
Extraction: OCR
OCR Confidence: 93.25%
Review: Not Required
```

## Delivery Note

```text
Document Type: DELIVERY_NOTE
Confidence: 92%
Extraction: Embedded Text
Review: Not Required
```

## Contract

```text
Document Type: CONTRACT
Confidence: 90%
Extraction: Embedded Text
Review: Not Required
```

---

# 🛠️ Technology Stack

| Component               | Technology                             |
| ----------------------- | -------------------------------------- |
| Programming Language    | Python                                 |
| Data Validation         | Pydantic                               |
| PDF Processing          | PyMuPDF                                |
| OCR Engine              | Tesseract OCR                          |
| OCR Integration         | pytesseract                            |
| Image Processing        | OpenCV                                 |
| Image Handling          | Pillow                                 |
| User Interface          | Streamlit                              |
| Document Classification | Rule-based weighted keyword classifier |
| Output Format           | Structured JSON                        |

---

# 💡 Design Decisions

## Why Rule-Based Classification?

The problem contains a small and clearly defined set of document categories:

* Invoice
* Delivery Note
* Contract

For this scope, a weighted keyword classifier provides a simple and effective solution.

### Advantages

* Explainable
* Deterministic
* Fast
* Easy to debug
* No model hosting required
* No external API dependency
* Easy to extend with additional keywords

The classifier also exposes matched keywords and scores, making its decisions transparent.

---

## Why Pydantic?

Pydantic provides explicit schemas and validation for extracted information.

Instead of returning arbitrary Python dictionaries, each document type follows a predefined structure.

This provides:

* Schema validation
* Type safety
* Consistent JSON output
* Easier debugging
* Predictable downstream integration

---

## Why OCR?

Vendor documents may be scanned or image-based rather than text-based PDFs.

The system therefore supports multiple extraction paths:

```text
Text-based PDF
      ↓
Embedded Text Extraction
```

```text
Scanned PDF
      ↓
PDF → Image
      ↓
Image Preprocessing
      ↓
OCR
      ↓
Extracted Text
```

```text
PNG / JPG / JPEG
      ↓
Image Preprocessing
      ↓
OCR
      ↓
Extracted Text
```

This allows the same overall pipeline to process both digital and scanned documents.

---

# 🔄 End-to-End Processing Flow

The complete processing pipeline can be summarized as:

```text
                    ┌─────────────────┐
                    │ Upload Document │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Validate Format │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Extract Text    │
                    │ or Run OCR      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Classify Type   │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
             Invoice    Delivery Note  Contract
                │            │            │
                └────────────┼────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Structured Data │
                    │   Extraction    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Pydantic        │
                    │ Validation      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Confidence &    │
                    │ Review Decision │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ JSON + Metadata │
                    └─────────────────┘
```

---

# 📌 Limitations

This implementation intentionally focuses on the requirements of **Problem 6** rather than attempting to build a general-purpose document intelligence platform.

Current limitations include:

* Rule-based extraction instead of semantic LLM-based extraction
* Limited document categories
* Template/layout variations outside the tested patterns may require additional extraction rules
* OCR accuracy depends on image quality and Tesseract configuration
* Date values are largely preserved in their source format
* Complex multi-page tables may require additional handling
* Highly unstructured documents may require additional extraction rules
* Confidence scoring is primarily document-level rather than field-level

These trade-offs keep the solution lightweight, explainable, deterministic, and easy to run locally.

---

# 🔮 Possible Future Improvements

If this system were extended beyond the current problem scope, possible improvements could include:

* ➕ Support for additional document types
* 📊 Advanced table detection
* 📅 Robust date normalization
* 🧠 Advanced entity extraction
* 🎯 Field-level confidence scoring
* 👤 Human-in-the-loop correction
* 📂 Batch folder processing
* ⚡ REST API using FastAPI
* 🧭 Layout-aware document models
* 🤖 LLM-based extraction for highly variable documents
* 🔎 Semantic document search
* 🗄️ Vector database integration
* 📈 Extraction quality monitoring
* 🧪 Automated evaluation datasets
* ☁️ Cloud deployment

These improvements are intentionally outside the current implementation to keep the solution focused on the stated requirements.

---

# ✅ Problem 6 Requirement Coverage

| Requirement               | Implementation                   |
| ------------------------- | -------------------------------- |
| Classify document type    | Weighted keyword classifier      |
| Structured JSON schema    | Pydantic models                  |
| Invoice extraction        | `InvoiceExtractor`               |
| Delivery note extraction  | `DeliveryNoteExtractor`          |
| Contract extraction       | `ContractExtractor`              |
| PDF support               | PyMuPDF                          |
| Image support             | Pillow + OCR                     |
| Scanned document handling | Tesseract OCR                    |
| Image preprocessing       | OpenCV                           |
| Format variation          | Multiple sample layouts          |
| Unusual document handling | `contract_unusual.pdf`           |
| Classification confidence | Weighted classification scoring  |
| OCR confidence            | Word-level OCR confidence        |
| Review flag               | `requires_review`                |
| Classification evidence   | Matched keyword evidence         |
| Interactive demonstration | Streamlit                        |
| JSON download             | Streamlit download functionality |

---

# 🧪 Testing Strategy

The project validates the pipeline against multiple document variations instead of testing only one document template.

### Test Categories

```text
                 ┌────────────────────┐
                 │    Test Dataset    │
                 └─────────┬──────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Standard          Variant          Scanned
      Documents         Layouts          Documents
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Classification     │
                 │ Extraction         │
                 │ OCR                │
                 │ Validation         │
                 └────────────────────┘
```

This approach helps verify that the implementation is not dependent on a single document layout.

---

# 📈 Why This Approach Works for Problem 6

The implementation intentionally balances **simplicity, robustness, explainability, and practical document-processing requirements**.

Instead of introducing unnecessary AI infrastructure, the system uses a focused pipeline:

```text
Document
   ↓
Text / OCR
   ↓
Classification
   ↓
Document-Specific Extraction
   ↓
Pydantic Validation
   ↓
Confidence / Review
   ↓
Structured JSON
```

This architecture makes the solution:

* Lightweight
* Deterministic
* Explainable
* Easy to test
* Easy to demonstrate
* Easy to extend
* Suitable for local execution

---

# 🚀 Future Production Architecture

For a larger production deployment, the current architecture could evolve into:

```text
                         ┌─────────────────────┐
                         │   Client / Frontend  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      REST API       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Document Processing  │
                         │      Pipeline        │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
                     ▼              ▼              ▼
                   OCR       Classification    Extraction
                     │              │              │
                     └──────────────┼──────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Schema Validation   │
                         │ + Confidence        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Database / Storage  │
                         └─────────────────────┘
```

The current implementation intentionally stops before this additional infrastructure to keep the Problem 6 solution focused and easy to evaluate.

---

# 📂 Sample Documents

The repository contains representative documents for each supported category:

```text
sample_data/
│
├── invoices/
│   ├── invoice_standard.pdf
│   ├── invoice_modern.pdf
│   └── invoice_scanned.png
│
├── delivery_notes/
│   ├── delivery_note_standard.pdf
│   └── delivery_note_landscape.pdf
│
└── contracts/
    ├── contract_simple.pdf
    ├── contract_standard.pdf
    └── contract_unusual.pdf
```

These samples demonstrate:

* Standard layouts
* Alternative layouts
* Different terminology
* Scanned documents
* OCR processing
* Classification variation
* Structured extraction

---

# 🔐 External Dependencies

The core application does **not** require:

* OpenAI API
* Gemini API
* Claude API
* Any paid LLM API
* Vector database
* Cloud AI service
* Model hosting infrastructure

The primary processing components run locally using Python libraries and Tesseract OCR.

---

# 📜 License

This project was developed as an implementation of **Problem 6: Document Extraction & Structuring Agent** for demonstration and evaluation purposes.

---

# 👨‍💻 Author

**Shaik Yaseen**

**B.Tech – Computer Science Engineering**

Focused on:

* Machine Learning
* AI Engineering
* Generative AI
* Intelligent Document Processing
* Python
* Computer Vision
* NLP

---

# ⭐ Project Summary

**Document Extraction & Structuring Agent** is a lightweight document intelligence pipeline capable of processing invoices, delivery notes, and contracts from both text-based and scanned documents.

The project demonstrates practical skills in:

```text
Document Processing
        +
OCR
        +
Computer Vision
        +
Rule-Based Classification
        +
Information Extraction
        +
Pydantic Validation
        +
Confidence Scoring
        +
Streamlit
```

The result is a **transparent, deterministic, locally executable document-processing system** that converts heterogeneous vendor documents into structured and validated JSON.
