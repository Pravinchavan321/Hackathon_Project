"""Expense Claim models and schemas."""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class ClaimStatus(str, Enum):
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SUBMITTED = "SUBMITTED"
    REJECTED = "REJECTED"
    DENIED = "DENIED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ExpenseCategory(str, Enum):
    TRAVEL = "travel"
    MEALS = "meals"
    LODGING = "lodging"
    TRANSPORT = "transport"
    SUPPLIES = "supplies"
    PERSONAL = "personal"
    ALCOHOL = "alcohol"
    GAMBLING = "gambling"
    GIFT_CARDS = "gift_cards"


class ClaimBase(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount (must be positive)")
    currency: str = Field(default="INR")
    category: str
    description: Optional[str] = ""
    merchant: Optional[str] = ""
    expense_date: Optional[str] = None


class ClaimCreate(ClaimBase):
    receipt_id: Optional[str] = None


class ClaimUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    merchant: Optional[str] = None


class ClaimResponse(ClaimBase):
    claim_id: str
    user_id: str
    status: ClaimStatus
    receipt_id: Optional[str] = None
    task_id: Optional[str] = None
    action_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ExpenseClaimInDB(ClaimResponse):
    idempotency_key: Optional[str] = None
