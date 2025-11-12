from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, func, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String(255), nullable=False)
    sku_lower = Column(String(255), nullable=False)
    name = Column(String(512))
    description = Column(String(1024))
    price = Column(Numeric(10,2))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("uq_sku_lower", "sku_lower", unique=True),)
