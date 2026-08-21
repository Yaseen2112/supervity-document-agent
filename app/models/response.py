from typing import Optional, Any, List, Literal
from pydantic import BaseModel, Field


class ExtractionIssue(BaseModel):
    field: Optional[str] = None
    reason: str


class DocumentResponse(BaseModel):
    document_id: str

    filename: str

    document_type: Literal[
        "invoice",
        "delivery_note",
        "contract",
        "unknown"
    ]

    classification_confidence: float = Field(
        ge=0,
        le=1
    )

    extraction_confidence: float = Field(
        ge=0,
        le=1
    )

    overall_confidence: float = Field(
        ge=0,
        le=1
    )

    status: Literal[
        "SUCCESS",
        "PARTIAL_EXTRACTION",
        "REVIEW_REQUIRED",
        "FAILED"
    ]

    review_required: bool

    data: Optional[Any] = None

    issues: List[ExtractionIssue] = Field(
        default_factory=list
    )