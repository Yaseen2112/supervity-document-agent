from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class DeliveryItem(BaseModel):
    description: Optional[str] = None

    ordered_quantity: Optional[float] = None
    delivered_quantity: Optional[float] = None

    unit: Optional[str] = None


class Recipient(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None


class DeliveryNote(BaseModel):
    document_type: Literal["delivery_note"] = "delivery_note"

    delivery_note_number: Optional[str] = None

    vendor_name: Optional[str] = None

    delivery_date: Optional[str] = None

    recipient: Optional[Recipient] = None

    items: List[DeliveryItem] = Field(default_factory=list)

    delivery_status: Optional[str] = None