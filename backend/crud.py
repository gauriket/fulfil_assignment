from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate


def upsert_product(db: Session, product: ProductCreate):
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
