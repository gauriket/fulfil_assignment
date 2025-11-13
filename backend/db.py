"""
Database connection and session management.

This module handles:
- PostgreSQL connection setup
- SQLAlchemy session creation and lifecycle
- Dependency injection for FastAPI endpoints

Uses scoped_session for thread-safe session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/products_db"
)

# Create engine with connection pooling and pre-ping to ensure connections are valid
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db():
    """
    FastAPI dependency to provide database sessions.
    
    This generator function creates a new database session for each request
    and ensures it's properly closed after the request completes.
    
    Usage in endpoints:
        @app.get("/products")
        def list_products(db: Session = Depends(get_db)):
            return db.query(Product).all()
    
    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
