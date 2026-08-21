from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class Contract(BaseModel):
    document_type: Literal["contract"] = "contract"

    contract_id: Optional[str] = None

    title: Optional[str] = None

    parties: List[str] = Field(default_factory=list)

    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None

    payment_terms: Optional[str] = None

    key_obligations: List[str] = Field(default_factory=list)

    termination_clause: Optional[str] = None