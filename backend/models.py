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

    __table_args__ = (Index("uq_sku_lower", "sku_lower", unique=True),)


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    event_types = Column(JSON, nullable=False)  # List of events as JSON
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# This will create all tables defined by Base subclasses
Base.metadata.create_all(bind=engine)
