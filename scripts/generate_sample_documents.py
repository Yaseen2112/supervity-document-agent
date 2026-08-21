from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from PIL import Image, ImageDraw, ImageFont, ImageFilter


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

SAMPLE_DIR = BASE_DIR / "sample_data"

INVOICE_DIR = SAMPLE_DIR / "invoices"
DELIVERY_DIR = SAMPLE_DIR / "delivery_notes"
CONTRACT_DIR = SAMPLE_DIR / "contracts"
LOW_QUALITY_DIR = SAMPLE_DIR / "low_quality"


# --------------------------------------------------
# CREATE DIRECTORIES
# --------------------------------------------------

def create_directories():
    directories = [
        INVOICE_DIR,
        DELIVERY_DIR,
        CONTRACT_DIR,
        LOW_QUALITY_DIR
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# STANDARD INVOICE
# --------------------------------------------------

def create_standard_invoice():

    file_path = INVOICE_DIR / "invoice_standard.pdf"

    c = canvas.Canvas(str(file_path), pagesize=A4)

    width, height = A4

    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 60, "INVOICE")

    c.setFont("Helvetica", 12)

    c.drawString(50, height - 100, "Vendor: TechSupply Solutions Pvt Ltd")
    c.drawString(50, height - 120, "Address: Hyderabad, India")

    c.drawString(350, height - 100, "Invoice Number: INV-2026-001")
    c.drawString(350, height - 120, "Invoice Date: 2026-08-21")
    c.drawString(350, height - 140, "Due Date: 2026-09-20")

    c.line(50, height - 180, 550, height - 180)

    c.setFont("Helvetica-Bold", 11)

    c.drawString(50, height - 205, "Description")
    c.drawString(250, height - 205, "Quantity")
    c.drawString(350, height - 205, "Unit Price")
    c.drawString(450, height - 205, "Total")

    c.line(50, height - 215, 550, height - 215)

    c.setFont("Helvetica", 11)

    items = [
        ("Laptop", 2, 50000, 100000),
        ("Wireless Mouse", 5, 1000, 5000),
        ("Keyboard", 3, 2000, 6000)
    ]

    y = height - 240

    for description, quantity, price, total in items:

        c.drawString(50, y, description)
        c.drawString(250, y, str(quantity))
        c.drawString(350, y, f"{price}")
        c.drawString(450, y, f"{total}")

        y -= 25

    c.line(50, y, 550, y)

    y -= 30

    c.drawString(350, y, "Subtotal:")
    c.drawString(450, y, "111000")

    y -= 25

    c.drawString(350, y, "Tax:")
    c.drawString(450, y, "19980")

    y -= 25

    c.setFont("Helvetica-Bold", 12)

    c.drawString(350, y, "Total Amount:")
    c.drawString(450, y, "130980 INR")

    c.save()

    print(f"Created: {file_path}")


# --------------------------------------------------
# MODERN / DIFFERENTLY FORMATTED INVOICE
# --------------------------------------------------

def create_modern_invoice():

    file_path = INVOICE_DIR / "invoice_modern.pdf"

    c = canvas.Canvas(str(file_path), pagesize=A4)

    width, height = A4

    c.setFillColor(colors.darkblue)
    c.rect(0, height - 100, width, 100, fill=1)

    c.setFillColor(colors.white)

    c.setFont("Helvetica-Bold", 28)
    c.drawString(40, height - 65, "TechSupply")

    c.setFont("Helvetica", 14)
    c.drawString(400, height - 60, "INVOICE")

    c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 13)

    c.drawString(50, height - 140, "BILL TO")

    c.setFont("Helvetica", 11)

    c.drawString(50, height - 165, "Supervity Demo Corporation")
    c.drawString(50, height - 185, "Bengaluru, India")

    c.setFont("Helvetica-Bold", 11)

    c.drawString(350, height - 140, "Invoice ID")
    c.drawString(350, height - 165, "Issued")
    c.drawString(350, height - 190, "Payment Due")

    c.setFont("Helvetica", 11)

    c.drawString(450, height - 140, "TS-INV-998")
    c.drawString(450, height - 165, "21 Aug 2026")
    c.drawString(450, height - 190, "20 Sep 2026")

    c.setFillColor(colors.lightgrey)
    c.rect(40, height - 260, 515, 30, fill=1)

    c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 10)

    c.drawString(50, height - 250, "ITEM")
    c.drawString(300, height - 250, "QTY")
    c.drawString(370, height - 250, "PRICE")
    c.drawString(470, height - 250, "AMOUNT")

    items = [
        ("Monitor", 4, 20000, 80000),
        ("USB-C Hub", 6, 3000, 18000)
    ]

    y = height - 290

    c.setFont("Helvetica", 11)

    for item, qty, price, amount in items:

        c.drawString(50, y, item)
        c.drawString(300, y, str(qty))
        c.drawString(370, y, str(price))
        c.drawString(470, y, str(amount))

        y -= 35

    y -= 30

    c.setFont("Helvetica-Bold", 12)

    c.drawString(350, y, "AMOUNT PAYABLE")
    c.drawString(470, y, "₹116,820")

    c.save()

    print(f"Created: {file_path}")


# --------------------------------------------------
# STANDARD DELIVERY NOTE
# --------------------------------------------------

def create_standard_delivery_note():

    file_path = DELIVERY_DIR / "delivery_note_standard.pdf"

    c = canvas.Canvas(str(file_path), pagesize=A4)

    width, height = A4

    c.setFont("Helvetica-Bold", 24)

    c.drawString(50, height - 60, "DELIVERY NOTE")

    c.setFont("Helvetica", 12)

    c.drawString(
        50,
        height - 100,
        "Vendor: TechSupply Solutions Pvt Ltd"
    )

    c.drawString(
        50,
        height - 125,
        "Delivery Note Number: DN-2026-001"
    )

    c.drawString(
        50,
        height - 150,
        "Delivery Date: 2026-08-21"
    )

    c.drawString(
        50,
        height - 175,
        "Deliver To: Supervity Demo Corporation"
    )

    c.drawString(
        50,
        height - 200,
        "Address: Bengaluru, India"
    )

    c.line(50, height - 240, 550, height - 240)

    c.setFont("Helvetica-Bold", 11)

    c.drawString(50, height - 265, "Item")
    c.drawString(250, height - 265, "Ordered Qty")
    c.drawString(370, height - 265, "Delivered Qty")
    c.drawString(500, height - 265, "Unit")

    c.line(50, height - 275, 550, height - 275)

    c.setFont("Helvetica", 11)

    items = [
        ("Laptop", 10, 10, "pieces"),
        ("Keyboard", 15, 12, "pieces"),
        ("Mouse", 20, 20, "pieces")
    ]

    y = height - 300

    for item, ordered, delivered, unit in items:

        c.drawString(50, y, item)
        c.drawString(250, y, str(ordered))
        c.drawString(390, y, str(delivered))
        c.drawString(500, y, unit)

        y -= 30

    y -= 20

    c.setFont("Helvetica-Bold", 12)

    c.drawString(
        50,
        y,
        "Delivery Status: PARTIAL"
    )

    c.save()

    print(f"Created: {file_path}")


# --------------------------------------------------
# LANDSCAPE DELIVERY NOTE
# --------------------------------------------------

def create_landscape_delivery_note():

    file_path = DELIVERY_DIR / "delivery_note_landscape.pdf"

    page_size = landscape(A4)

    c = canvas.Canvas(
        str(file_path),
        pagesize=page_size
    )

    width, height = page_size

    c.setFont("Helvetica-Bold", 26)

    c.drawString(
        50,
        height - 60,
        "GOODS DELIVERY RECORD"
    )

    c.setFont("Helvetica", 12)

    c.drawString(
        50,
        height - 110,
        "Reference: DEL-99821"
    )

    c.drawString(
        50,
        height - 135,
        "Supplier: Global Hardware Ltd"
    )

    c.drawString(
        50,
        height - 160,
        "Date Delivered: August 21, 2026"
    )

    c.drawString(
        450,
        height - 110,
        "Receiving Company: Supervity Demo Corp"
    )

    c.drawString(
        450,
        height - 135,
        "Location: Bengaluru Warehouse"
    )

    c.line(50, height - 200, 790, height - 200)

    c.setFont("Helvetica-Bold", 11)

    c.drawString(50, height - 230, "PRODUCT")
    c.drawString(350, height - 230, "REQUESTED")
    c.drawString(500, height - 230, "RECEIVED")
    c.drawString(650, height - 230, "UNIT")

    c.setFont("Helvetica", 11)

    items = [
        ("External Monitor", 20, 20, "pcs"),
        ("Docking Station", 10, 10, "pcs")
    ]

    y = height - 270

    for item, requested, received, unit in items:

        c.drawString(50, y, item)
        c.drawString(370, y, str(requested))
        c.drawString(520, y, str(received))
        c.drawString(650, y, unit)

        y -= 40

    c.setFont("Helvetica-Bold", 12)

    c.drawString(
        50,
        y - 30,
        "Status: COMPLETE"
    )

    c.save()

    print(f"Created: {file_path}")


# --------------------------------------------------
# STANDARD CONTRACT
# --------------------------------------------------

def create_standard_contract():

    file_path = CONTRACT_DIR / "contract_standard.pdf"

    c = canvas.Canvas(str(file_path), pagesize=A4)

    width, height = A4

    c.setFont("Helvetica-Bold", 20)

    c.drawCentredString(
        width / 2,
        height - 70,
        "SOFTWARE SERVICES AGREEMENT"
    )

    text = c.beginText(50, height - 120)

    text.setFont("Helvetica", 11)
    text.setLeading(20)

    lines = [
        "Contract ID: CTR-2026-001",
        "",
        "This Software Services Agreement is entered into between",
        "TechSupply Solutions Pvt Ltd and Supervity Demo Corporation.",
        "",
        "Effective Date: January 1, 2026",
        "Expiry Date: December 31, 2026",
        "",
        "Payment Terms: Net 30 days from invoice date.",
        "",
        "Key Obligations:",
        "1. TechSupply Solutions will provide agreed software services.",
        "2. Both parties must maintain confidentiality.",
        "3. Services will be delivered according to agreed milestones.",
        "",
        "Termination:",
        "Either party may terminate this agreement with 30 days written notice."
    ]

    for line in lines:
        text.textLine(line)

    c.drawText(text)

    c.save()

    print(f"Created: {file_path}")


# --------------------------------------------------
# SIMPLE CONTRACT
# --------------------------------------------------

def create_simple_contract():

    file_path = CONTRACT_DIR / "contract_simple.pdf"

    c = canvas.Canvas(str(file_path), pagesize=A4)

    width, height = A4

    c.setFont("Helvetica-Bold", 22)

    c.drawString(
        50,
        height - 60,
        "SERVICE CONTRACT"
    )

    c.setFont("Helvetica", 12)

    lines = [
        ("Agreement Number", "SC-2026-882"),
        ("Party One", "Global Hardware Ltd"),
        ("Party Two", "Supervity Demo Corporation"),
        ("Start Date", "2026-08-01"),
        ("End Date", "2027-07-31"),
        ("Payment", "Payment within 15 days"),
        ("Termination", "14 days written notice required")
    ]

    y = height - 120

    for label, value in lines:

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{label}:")

        c.setFont("Helvetica", 12)
        c.drawString(220, y, value)

        y -= 40

    c.setFont("Helvetica-Bold", 12)

    c.drawString(
        50,
        y,
        "Responsibilities:"
    )

    y -= 30

    c.setFont("Helvetica", 11)

    responsibilities = [
        "Provide requested hardware support.",
        "Maintain agreed service levels.",
        "Report major incidents within 24 hours."
    ]

    for responsibility in responsibilities:

        c.drawString(
            70,
            y,
            f"- {responsibility}"
        )

        y -= 25

    c.save()

    print(f"Created: {file_path}")


# --------------------------------------------------
# UNUSUAL CONTRACT
# --------------------------------------------------

def create_unusual_contract():

    file_path = CONTRACT_DIR / "contract_unusual.pdf"

    c = canvas.Canvas(str(file_path), pagesize=A4)

    width, height = A4

    c.setFont("Helvetica-Bold", 18)

    c.drawString(
        50,
        height - 60,
        "MEMORANDUM OF COMMERCIAL TERMS"
    )

    text = c.beginText(50, height - 110)

    text.setFont("Helvetica", 11)
    text.setLeading(22)

    lines = [
        "Reference Code: MCT-441-2026",
        "",
        "Participants: Alpha Logistics India Pvt Ltd | Supervity Demo Corp",
        "",
        "This memorandum becomes active on 15 August 2026.",
        "The commercial arrangement concludes on 14 August 2027.",
        "",
        "Settlement condition: invoices payable thirty days after receipt.",
        "",
        "Alpha Logistics shall provide transportation coordination.",
        "Supervity Demo Corp shall provide accurate shipment information.",
        "",
        "Exit provision: either participant may discontinue the arrangement",
        "after providing thirty calendar days written notification."
    ]

    for line in lines:
        text.textLine(line)

    c.drawText(text)

    c.save()

    print(f"Created: {file_path}")


# --------------------------------------------------
# LOW QUALITY INVOICE IMAGE
# --------------------------------------------------

def create_low_quality_invoice():

    file_path = LOW_QUALITY_DIR / "invoice_low_quality.png"

    width = 1000
    height = 1400

    image = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(image)

    try:
        font_large = ImageFont.truetype(
            "arial.ttf",
            48
        )

        font_medium = ImageFont.truetype(
            "arial.ttf",
            28
        )

    except OSError:

        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    draw.text(
        (60, 50),
        "INVOICE",
        fill="black",
        font=font_large
    )

    lines = [
        "Vendor: TechSupply Solutions",
        "Invoice Number: INV-LOW-001",
        "Invoice Date: 2026-08-21",
        "",
        "Laptop        Qty: 2        50000",
        "Keyboard      Qty: 3        2000",
        "Mouse         Qty: 5        1000",
        "",
        "Total Amount: 111000 INR"
    ]

    y = 180

    for line in lines:

        draw.text(
            (60, y),
            line,
            fill="black",
            font=font_medium
        )

        y += 80

    # Add blur
    image = image.filter(
        ImageFilter.GaussianBlur(radius=2.5)
    )

    # Reduce resolution
    image = image.resize(
        (500, 700)
    )

    # Slight rotation
    image = image.rotate(
        2,
        expand=True,
        fillcolor="white"
    )

    image.save(file_path)

    print(f"Created: {file_path}")


# --------------------------------------------------
# SCANNED INVOICE PNG
# --------------------------------------------------

def create_scanned_invoice():

    file_path = INVOICE_DIR / "invoice_scanned.png"

    width = 1200
    height = 1600

    # Slight off-white background to simulate a scanned paper document
    image = Image.new(
        "RGB",
        (width, height),
        (248, 248, 245)
    )

    draw = ImageDraw.Draw(image)

    # Try to use Arial; fallback if unavailable
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 52)
        font_bold = ImageFont.truetype("arialbd.ttf", 30)
        font_medium = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 24)

    except OSError:
        font_title = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Header
    draw.text(
        (70, 60),
        "INVOICE",
        fill=(20, 20, 20),
        font=font_title
    )

    draw.line(
        [(70, 140), (1130, 140)],
        fill=(80, 80, 80),
        width=3
    )

    # Vendor details
    draw.text(
        (70, 180),
        "TechSupply Solutions Pvt Ltd",
        fill=(20, 20, 20),
        font=font_bold
    )

    draw.text(
        (70, 225),
        "45, HITEC City, Hyderabad, India",
        fill=(40, 40, 40),
        font=font_small
    )

    draw.text(
        (70, 260),
        "GSTIN: 36ABCDE1234F1Z5",
        fill=(40, 40, 40),
        font=font_small
    )

    # Invoice metadata
    draw.text(
        (700, 185),
        "Invoice No:",
        fill=(20, 20, 20),
        font=font_bold
    )

    draw.text(
        (930, 185),
        "SCAN-2026-001",
        fill=(20, 20, 20),
        font=font_medium
    )

    draw.text(
        (700, 235),
        "Invoice Date:",
        fill=(20, 20, 20),
        font=font_bold
    )

    draw.text(
        (930, 235),
        "21-08-2026",
        fill=(20, 20, 20),
        font=font_medium
    )

    draw.text(
        (700, 285),
        "Due Date:",
        fill=(20, 20, 20),
        font=font_bold
    )

    draw.text(
        (930, 285),
        "20-09-2026",
        fill=(20, 20, 20),
        font=font_medium
    )

    # Bill To
    draw.text(
        (70, 370),
        "BILL TO",
        fill=(20, 20, 20),
        font=font_bold
    )

    draw.text(
        (70, 415),
        "Supervity Demo Corporation",
        fill=(30, 30, 30),
        font=font_medium
    )

    draw.text(
        (70, 455),
        "Bengaluru, Karnataka, India",
        fill=(40, 40, 40),
        font=font_small
    )

    # Table header
    table_top = 540

    draw.rectangle(
        [(70, table_top), (1130, table_top + 55)],
        outline=(50, 50, 50),
        width=2
    )

    headers = [
        ("Description", 90),
        ("Qty", 550),
        ("Unit Price", 700),
        ("Amount", 930)
    ]

    for text, x in headers:
        draw.text(
            (x, table_top + 12),
            text,
            fill=(20, 20, 20),
            font=font_bold
        )

    # Table rows
    items = [
        ("Laptop", "2", "50000", "100000"),
        ("Wireless Keyboard", "3", "2500", "7500"),
        ("Wireless Mouse", "5", "1200", "6000")
    ]

    y = table_top + 55

    for description, quantity, price, amount in items:

        draw.rectangle(
            [(70, y), (1130, y + 65)],
            outline=(100, 100, 100),
            width=1
        )

        draw.text((90, y + 17), description, fill=(30, 30, 30), font=font_medium)
        draw.text((560, y + 17), quantity, fill=(30, 30, 30), font=font_medium)
        draw.text((710, y + 17), price, fill=(30, 30, 30), font=font_medium)
        draw.text((950, y + 17), amount, fill=(30, 30, 30), font=font_medium)

        y += 65

    # Totals
    y += 80

    totals = [
        ("Subtotal:", "113500"),
        ("Tax (18%):", "20430"),
        ("Total Amount:", "133930 INR")
    ]

    for label, value in totals:

        draw.text(
            (700, y),
            label,
            fill=(20, 20, 20),
            font=font_bold
        )

        draw.text(
            (930, y),
            value,
            fill=(20, 20, 20),
            font=font_medium
        )

        y += 60

    # Add a very slight blur/noise effect to look like a scan,
    # while still keeping it readable.
    image = image.filter(
        ImageFilter.GaussianBlur(radius=0.3)
    )

    # Slight rotation to simulate scanning
    image = image.rotate(
        0.5,
        expand=True,
        fillcolor=(248, 248, 245)
    )

    image.save(file_path)

    print(f"Created: {file_path}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\nCreating sample documents...\n")

    create_directories()

    create_standard_invoice()
    create_modern_invoice()
    create_scanned_invoice()

    create_standard_delivery_note()
    create_landscape_delivery_note()

    create_standard_contract()
    create_simple_contract()
    create_unusual_contract()

    create_low_quality_invoice()

    print("\nAll sample documents created successfully!")


if __name__ == "__main__":
    main()