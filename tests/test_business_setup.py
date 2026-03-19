"""Test script for business setup & compliance module."""
import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.compliance_service import get_compliance_service
from app.services.invoice_service import get_invoice_service
from app.services.eboekhouden_service import get_eboekhouden_client
from app.models.invoice import InvoiceStatus
from decimal import Decimal


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")


def test_legal_documents():
    """Test legal document endpoints."""
    print_header("Testing Legal Documents")
    
    service = get_compliance_service()
    
    try:
        # Test getting Terms of Service
        doc = service.get_legal_document("terms", format="markdown")
        print_success(f"Terms of Service loaded: {len(doc['content'])} chars")
        print_info(f"Last updated: {doc['last_updated']}")
        
        # Test getting Privacy Policy
        doc = service.get_legal_document("privacy", format="markdown")
        print_success(f"Privacy Policy loaded: {len(doc['content'])} chars")
        
        # Test getting DPA
        doc = service.get_legal_document("dpa", format="markdown")
        print_success(f"DPA loaded: {len(doc['content'])} chars")
        
        # Test getting Cookie Policy
        doc = service.get_legal_document("cookies", format="markdown")
        print_success(f"Cookie Policy loaded: {len(doc['content'])} chars")
        
        # Test listing all documents
        docs = service.list_legal_documents()
        print_success(f"Listed {len(docs)} legal documents")
        
        return True
    except Exception as e:
        print_error(f"Legal documents test failed: {e}")
        return False


def test_invoice_generation():
    """Test invoice generation."""
    print_header("Testing Invoice Generation")
    
    service = get_invoice_service()
    
    try:
        # Test creating invoice from payment
        invoice = service.create_invoice_from_payment(
            payment_id="test_payment_123",
            provider="stripe",
            amount=Decimal("100.00"),
            currency="EUR",
            customer_name="Test Customer",
            customer_email="test@example.com",
            customer_address="123 Test St, Amsterdam",
            description="Test payment",
        )
        
        print_success(f"Invoice created: {invoice.invoice_number}")
        print_info(f"Invoice ID: {invoice.invoice_id}")
        print_info(f"Amount: €{invoice.total_incl_vat}")
        print_info(f"Status: {invoice.status.value}")
        
        # Test getting invoice
        retrieved = service.get_invoice(invoice.invoice_id)
        if retrieved:
            print_success("Invoice retrieved successfully")
        else:
            print_error("Failed to retrieve invoice")
            return False
        
        # Test listing invoices
        invoice_list = service.list_invoices(limit=10)
        print_success(f"Listed {invoice_list['total']} invoices")
        
        # Test HTML rendering
        html = service.render_invoice_html(invoice)
        print_success(f"Invoice HTML rendered: {len(html)} chars")
        
        return True
    except Exception as e:
        print_error(f"Invoice generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_eboekhouden():
    """Test e-boekhouden integration."""
    print_header("Testing e-boekhouden Integration")
    
    client = get_eboekhouden_client()
    
    if not client.enabled:
        print_info("e-boekhouden sync is disabled (EBOEKHOUDEN_SYNC_ENABLED=false)")
        print_info("To enable: Set EBOEKHOUDEN_SYNC_ENABLED=true and configure API credentials")
        return True
    
    if not client.api_key or not client.company_id:
        print_error("e-boekhouden API credentials not configured")
        print_info("Set EBOEKHOUDEN_API_KEY and EBOEKHOUDEN_COMPANY_ID environment variables")
        return False
    
    try:
        # Test connection
        print_info("Testing e-boekhouden connection...")
        result = await client.test_connection()
        if result.get("success"):
            print_success("e-boekhouden connection successful")
        else:
            print_error(f"e-boekhouden connection failed: {result.get('error')}")
            return False
        
        return True
    except Exception as e:
        print_error(f"e-boekhouden test failed: {e}")
        print_info("Note: This is expected if e-boekhouden API is not configured")
        return False


def test_environment_variables():
    """Test environment variable configuration."""
    print_header("Checking Environment Variables")
    
    required_vars = {
        "Company Info": [
            "COMPANY_NAME",
            "COMPANY_KVK_NUMBER",
            "COMPANY_BTW_NUMBER",
            "COMPANY_EMAIL",
        ],
        "Branding": [
            "BRANDING_PRIMARY_COLOR",
            "BRANDING_FONT_FAMILY",
        ],
        "e-boekhouden": [
            "EBOEKHOUDEN_SYNC_ENABLED",
        ],
    }
    
    all_ok = True
    for category, vars_list in required_vars.items():
        print_info(f"\n{category}:")
        for var in vars_list:
            value = os.getenv(var)
            if value:
                print_success(f"  {var}: {'***' if 'KEY' in var or 'SECRET' in var else value}")
            else:
                print_error(f"  {var}: Not set")
                if var != "EBOEKHOUDEN_SYNC_ENABLED":
                    all_ok = False
    
    optional_vars = [
        "COMPANY_BANK_ACCOUNT",
        "COMPANY_ADDRESS",
        "COMPANY_DOMAIN",
        "BRANDING_LOGO_URL",
        "EBOEKHOUDEN_API_KEY",
        "EBOEKHOUDEN_COMPANY_ID",
    ]
    
    print_info("\nOptional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print_success(f"  {var}: {'***' if 'KEY' in var or 'SECRET' in var else value}")
        else:
            print_info(f"  {var}: Not set (optional)")
    
    return all_ok


async def main():
    """Run all tests."""
    print_header("Business Setup & Compliance Module - Test Suite")
    
    results = []
    
    # Test environment variables
    results.append(("Environment Variables", test_environment_variables()))
    
    # Test legal documents
    results.append(("Legal Documents", test_legal_documents()))
    
    # Test invoice generation
    results.append(("Invoice Generation", test_invoice_generation()))
    
    # Test e-boekhouden (async)
    results.append(("e-boekhouden Integration", await test_eboekhouden()))
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\n{'=' * 60}")
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60 + "\n")
    
    if passed == total:
        print_success("All tests passed! 🎉")
        return 0
    else:
        print_error("Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

