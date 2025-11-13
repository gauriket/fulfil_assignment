from pydantic import BaseModel, HttpUrl
from typing import List, Optional
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


class WebhookBase(BaseModel):
    url: HttpUrl
    event_types: List[str]
    active: Optional[bool] = True


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl]
    event_types: Optional[List[str]]
    active: Optional[bool]


class WebhookOut(WebhookBase):
    id: int
