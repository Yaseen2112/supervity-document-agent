from app.models.invoice import Invoice, Vendor, InvoiceLineItem
from app.models.delivery_note import DeliveryNote, DeliveryItem
from app.models.contract import Contract


def test_invoice():

    invoice = Invoice(
        vendor=Vendor(
            name="ABC Supplies",
            address="Hyderabad, India"
        ),
        invoice_number="INV-1001",
        invoice_date="2026-08-21",
        currency="INR",
        line_items=[
            InvoiceLineItem(
                description="Laptop",
                quantity=2,
                unit_price=50000,
                total=100000
            )
        ],
        subtotal=100000,
        tax=18000,
        total_amount=118000
    )

    print(invoice.model_dump_json(indent=2))


def test_delivery_note():

    delivery = DeliveryNote(
        delivery_note_number="DN-1001",
        vendor_name="ABC Supplies",
        items=[
            DeliveryItem(
                description="Laptop",
                ordered_quantity=10,
                delivered_quantity=8,
                unit="pieces"
            )
        ],
        delivery_status="partial"
    )

    print(delivery.model_dump_json(indent=2))


def test_contract():

    contract = Contract(
        contract_id="CTR-1001",
        title="Software Services Agreement",
        parties=[
            "ABC Corp",
            "XYZ Technologies"
        ],
        effective_date="2026-01-01",
        expiry_date="2027-01-01"
    )

    print(contract.model_dump_json(indent=2))


if __name__ == "__main__":

    test_invoice()

    test_delivery_note()

    test_contract()