from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ProductCreate(BaseModel):
    sku: str
    name: Optional[str]
    description: Optional[str]
    price: Optional[Decimal]
    active: Optional[bool] = True


class ProductOut(BaseModel):
    sku: str
    name: str
    description: str | None
    price: float | None
    active: bool

    model_config = {
        "from_attributes": True  # <-- Allows reading from SQLAlchemy objects
    }


class ProductIn(BaseModel):
    sku: str
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    active: Optional[bool] = True
