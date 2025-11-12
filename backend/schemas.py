from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class ProductCreate(BaseModel):
    sku: str
    name: Optional[str]
    description: Optional[str]
    price: Optional[Decimal]
    active: Optional[bool] = True
