from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class InvoiceLineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


class Vendor(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None


class Invoice(BaseModel):
    document_type: Literal["invoice"] = "invoice"

    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None

    vendor: Optional[Vendor] = None

    customer_name: Optional[str] = None
    customer_address: Optional[str] = None

    currency: Optional[str] = None

    line_items: List[InvoiceLineItem] = Field(default_factory=list)

    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None