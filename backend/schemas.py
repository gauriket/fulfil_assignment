"""
Pydantic schemas for request/response validation.

This module defines data validation schemas for:
- Product creation and updates
- Webhook configuration and management

Schemas use Pydantic v2 with proper type hints and validation.
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from decimal import Decimal


class ProductCreate(BaseModel):
    """
    Schema for creating a new product.
    
    Used when accepting product data from API requests.
    SKU is required; other fields are optional.
    
    Attributes:
        sku (str): Stock Keeping Unit - unique identifier.
        name (Optional[str]): Product name.
        description (Optional[str]): Product description.
        price (Optional[Decimal]): Product price.
        active (Optional[bool]): Active status. Defaults to True.
    """
    sku: str
    name: Optional[str]
    description: Optional[str]
    price: Optional[Decimal]
    active: Optional[bool] = True


class ProductOut(BaseModel):
    """
    Schema for returning product data in API responses.
    
    Uses from_attributes=True to allow reading from SQLAlchemy ORM objects.
    
    Attributes:
        sku (str): Stock Keeping Unit.
        name (str): Product name.
        description (Optional[str]): Product description.
        price (Optional[float]): Product price.
        active (bool): Whether the product is active.
    """
    sku: str
    name: str
    description: str | None
    price: float | None
    active: bool

    model_config = {
        "from_attributes": True  # Allows reading from SQLAlchemy objects
    }


class ProductIn(BaseModel):
    """
    Schema for updating an existing product.
    
    All fields are optional to support partial updates.
    
    Attributes:
        sku (Optional[str]): Updated SKU.
        name (Optional[str]): Updated name.
        description (Optional[str]): Updated description.
        price (Optional[float]): Updated price.
        active (Optional[bool]): Updated active status.
    """
    sku: str
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    active: Optional[bool] = True


class WebhookBase(BaseModel):
    """
    Base schema for webhook configuration.
    
    Contains common fields shared by create and update operations.
    
    Attributes:
        url (HttpUrl): The webhook endpoint URL.
        event_types (List[str]): List of event types to subscribe to.
        active (Optional[bool]): Whether the webhook is active. Defaults to True.
    """
    url: HttpUrl
    event_types: List[str]
    active: Optional[bool] = True


class WebhookCreate(WebhookBase):
    """Schema for creating a new webhook."""
    pass


class WebhookUpdate(BaseModel):
    """
    Schema for updating an existing webhook.
    
    All fields are optional to support partial updates.
    
    Attributes:
        url (Optional[HttpUrl]): Updated webhook URL.
        event_types (Optional[List[str]]): Updated event types.
        active (Optional[bool]): Updated active status.
    """
    url: Optional[HttpUrl]
    event_types: Optional[List[str]]
    active: Optional[bool]


class WebhookOut(WebhookBase):
    """
    Schema for returning webhook data in API responses.
    
    Attributes:
        id (int): Unique webhook identifier.
        url (HttpUrl): The webhook endpoint URL.
        event_types (List[str]): Subscribed event types.
        active (bool): Whether the webhook is active.
    """
    id: int
