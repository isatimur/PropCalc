"""
Transaction domain model
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    SALE = "sale"
    RENTAL = "rental"
    MORTGAGE = "mortgage"
    LEASE = "lease"

class Transaction(BaseModel):
    """Transaction domain model"""
    id: int | None = None
    property_id: int = Field(..., description="Property ID")
    transaction_type: TransactionType = Field(TransactionType.SALE, description="Transaction type")
    price: float = Field(..., description="Transaction price")
    date: datetime = Field(..., description="Transaction date")
    buyer: str | None = Field(None, description="Buyer name")
    seller: str | None = Field(None, description="Seller name")
    created_at: datetime | None = Field(None, description="Creation timestamp")

    class Config:
        from_attributes = True
