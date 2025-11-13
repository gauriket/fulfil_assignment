"""
CRUD (Create, Read, Update, Delete) operations for products.

This module provides database operations for the Product model.
Currently focuses on upsert operations used during CSV imports.
"""

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate


def upsert_product(db: Session, product: ProductCreate):
    """
    Insert or update a product using PostgreSQL's ON CONFLICT clause.
    
    This operation uses the sku_lower unique index to detect existing products.
    If a product with the same SKU (case-insensitive) already exists,
    it updates the name, description, price, and active status.
    If it's new, it creates a new product record.
    
    This is the primary method used during CSV imports for efficiency.
    
    Args:
        db (Session): SQLAlchemy database session.
        product (ProductCreate): Product data to insert or update.
        
    Note:
        The sku_lower field is automatically derived from sku and stored in lowercase.
        This enables case-insensitive product identification while maintaining
        the original SKU casing.
    """
    stmt = insert(Product).values(
        sku=product.sku,
        sku_lower=product.sku.lower(),
        name=product.name,
        description=product.description,
        price=product.price,
        active=product.active if product.active is not None else True,
    )
    update_cols = {
        "name": stmt.excluded.name,
        "description": stmt.excluded.description,
        "price": stmt.excluded.price,
        "active": stmt.excluded.active,
    }
    stmt = stmt.on_conflict_do_update(index_elements=["sku_lower"], set_=update_cols)
    db.execute(stmt)
