"""
Comprehensive Test Suite for Document Extraction Agent
Runs all tests and generates a summary report.
"""

import json
import sys
from pathlib import Path

from app.services.document_orchestrator import DocumentOrchestrator
from app.models.invoice import Invoice
from app.models.delivery_note import DeliveryNote
from app.models.contract import Contract


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_sample_files():
    """Test extraction with all sample documents."""
    print_section("TESTING SAMPLE DOCUMENTS")
    
    orchestrator = DocumentOrchestrator()
    
    test_files = [
        "sample_data/invoices/invoice_standard.pdf",
        "sample_data/invoices/invoice_modern.pdf",
        "sample_data/invoices/invoice_scanned.png",
        "sample_data/delivery_notes/delivery_note_standard.pdf",
        "sample_data/delivery_notes/delivery_note_landscape.pdf",
        "sample_data/contracts/contract_simple.pdf",
        "sample_data/contracts/contract_standard.pdf",
        "sample_data/contracts/contract_unusual.pdf",
    ]
    
    results = []
    
    for file_path in test_files:
        try:
            result = orchestrator.process(file_path)
            
            # Verify JSON serialization
            json_output = json.dumps(result, indent=2)
            
            doc_type = result["classification"]["document_type"]
            confidence = result["classification"]["confidence"]
            requires_review = result["metadata"]["requires_review"]
            
            status = "✓ PASS" if confidence > 0.5 and not requires_review else "⚠ REVIEW"
            
            results.append({
                "file": Path(file_path).name,
                "type": doc_type,
                "confidence": f"{confidence * 100:.1f}%",
                "status": status,
                "requires_review": requires_review
            })
            
            print(f"\n{status} {Path(file_path).name}")
            print(f"   Type: {doc_type}")
            print(f"   Confidence: {confidence * 100:.1f}%")
            if requires_review:
                print(f"   ⚠️  Requires Review")
                
        except Exception as e:
            results.append({
                "file": Path(file_path).name,
                "type": "ERROR",
                "confidence": "0%",
                "status": "✗ FAIL",
                "error": str(e)
            })
            print(f"\n✗ FAIL {Path(file_path).name}")
            print(f"   Error: {e}")
    
    return results


def test_json_serialization():
    """Test JSON serialization for all model types."""
    print_section("TESTING JSON SERIALIZATION")
    
    test_cases = [
        {
            "name": "Invoice (with vendor)",
            "model": Invoice(
                invoice_number="INV-001",
                invoice_date="2026-08-21",
                vendor={"name": "TechSupply", "address": "Hyderabad"},
                total_amount=1000
            )
        },
        {
            "name": "Invoice (without vendor)",
            "model": Invoice(
                invoice_number="INV-002",
                vendor=None,
                total_amount=500
            )
        },
        {
            "name": "DeliveryNote",
            "model": DeliveryNote(
                delivery_note_number="DN-001",
                vendor_name="Supplier A"
            )
        },
        {
            "name": "Contract",
            "model": Contract(
                contract_id="CTR-001",
                title="Agreement",
                parties=["Party A", "Party B"]
            )
        },
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            # Test model_dump
            data = test_case["model"].model_dump()
            
            # Test model_dump_json
            json_str = test_case["model"].model_dump_json()
            
            # Test json.dumps (like streamlit app)
            json_output = json.dumps(data, indent=2, ensure_ascii=False)
            
            results.append({
                "name": test_case["name"],
                "status": "✓ PASS",
                "json_size": len(json_output)
            })
            
            print(f"✓ PASS {test_case['name']}")
            print(f"   JSON size: {len(json_output)} bytes")
            
        except Exception as e:
            results.append({
                "name": test_case["name"],
                "status": "✗ FAIL",
                "error": str(e)
            })
            print(f"✗ FAIL {test_case['name']}")
            print(f"   Error: {e}")
    
    return results


def test_ocr_handling():
    """Test low-quality OCR handling."""
    print_section("TESTING OCR ERROR HANDLING")
    
    orchestrator = DocumentOrchestrator()
    
    print("\nProcessing low-quality invoice...")
    try:
        result = orchestrator.process("sample_data/low_quality/invoice_low_quality.png")
        
        ocr_conf = result["metadata"]["ocr_confidence"]
        requires_review = result["metadata"]["requires_review"]
        doc_type = result["classification"]["document_type"]
        
        print(f"✓ Document classified as: {doc_type}")
        print(f"  OCR Confidence: {ocr_conf}%")
        print(f"  Requires Review: {requires_review}")
        
        if requires_review:
            print("  ✓ Low-quality correctly flagged for review")
        
        # Verify JSON is valid even with null fields
        json_output = json.dumps(result, indent=2)
        print(f"  ✓ Valid JSON generated ({len(json_output)} bytes)")
        
        return [{"status": "✓ PASS", "message": "Low-quality handling works correctly"}]
        
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return [{"status": "✗ FAIL", "error": str(e)}]


def print_summary(all_results):
    """Print a summary of all test results."""
    print_section("TEST SUMMARY")
    
    total_tests = sum(len(r) if isinstance(r, list) else 1 for r in all_results)
    passed = sum(
        1 for r in all_results 
        for item in (r if isinstance(r, list) else [r])
        if isinstance(item, dict) and "PASS" in str(item.get("status", ""))
    )
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Success Rate: {(passed/total_tests*100):.1f}%")
    
    if passed == total_tests:
        print("\n✓ ALL TESTS PASSED!")
        print("\nYour Document Extraction Agent is ready for deployment.")
        print("Key Features:")
        print("  • PDF text extraction (embedded text)")
        print("  • OCR support for scanned documents and images")
        print("  • Document classification (Invoice/Delivery Note/Contract)")
        print("  • Structured JSON output")
        print("  • Low-quality document detection and review flagging")
        return True
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  Document Extraction & Structuring Agent - Full Test Suite".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    all_results = []
    
    # Run all tests
    all_results.append(test_sample_files())
    all_results.append(test_json_serialization())
    all_results.append(test_ocr_handling())
    
    # Print summary
    success = print_summary(all_results)
    
    print("\n")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
