"""
SQLAlchemy ORM models for the product management system.

This module defines the database models:
- Product: Stores product information with SKU-based uniqueness
- Webhook: Stores webhook configurations for event notifications

Models use PostgreSQL-specific features like JSONB for efficient querying.
"""

import os
from sqlalchemy import (
    JSON,
    Column,
    Integer,
    String,
    Boolean,
    Numeric,
    DateTime,
    create_engine,
    func,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/products_db"
)
engine = create_engine(DATABASE_URL)


class Product(Base):
    """
    Product model for storing product information.
    
    Uses a unique index on sku_lower for case-insensitive SKU lookups.
    Timestamps are automatically managed by the database.
    
    Attributes:
        id (int): Primary key, auto-generated.
        sku (str): Stock Keeping Unit - unique identifier for the product.
        sku_lower (str): Lowercase version of SKU for case-insensitive searches (unique).
        name (str, optional): Product name.
        description (str, optional): Product description.
        price (Decimal): Product price with 2 decimal places.
        active (bool): Whether the product is active. Defaults to True.
        created_at (DateTime): Timestamp when the product was created.
        updated_at (DateTime): Timestamp when the product was last updated.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String(255), nullable=False)
    sku_lower = Column(String(255), nullable=False)
    name = Column(String(512))
    description = Column(String(1024))
    price = Column(Numeric(10, 2))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Unique index on sku_lower for case-insensitive uniqueness
    __table_args__ = (Index("uq_sku_lower", "sku_lower", unique=True),)


class Webhook(Base):
    """
    Webhook model for storing webhook configurations.
    
    Webhooks are used to send notifications to external systems when
    certain events occur (e.g., product import completion).
    
    Attributes:
        id (int): Primary key, auto-generated.
        url (str): The URL endpoint to send webhook notifications to.
        event_types (JSON): List of event types this webhook is subscribed to.
        active (bool): Whether the webhook is currently active. Defaults to True.
        created_at (DateTime): Timestamp when the webhook was created.
        updated_at (DateTime): Timestamp when the webhook was last updated.
    """
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    event_types = Column(JSON, nullable=False)  # List of events as JSON
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# Create all tables defined by Base subclasses
Base.metadata.create_all(bind=engine)
