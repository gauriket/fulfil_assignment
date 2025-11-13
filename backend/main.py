"""
FastAPI application for product management with CSV import functionality.

This module provides the main API endpoints for:
- CSV file uploads with real-time progress tracking
- Product CRUD operations (Create, Read, Update, Delete)
- Job status polling for import operations
- Webhook management (via webhook module)

Features:
- Asynchronous file uploads with background processing
- Real-time progress tracking via job status endpoint
- Case-insensitive product search by SKU, name, and description
- CORS support for frontend integration
"""

from typing import List, Optional
from fastapi import BackgroundTasks, Depends, FastAPI, UploadFile, File, HTTPException
import os, uuid, aiofiles
from models import Product
from db import get_db
from schemas import ProductCreate, ProductIn, ProductOut
from tasks import import_csv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import webhook
from tasks import job_status

app = FastAPI(
    title="Product Management API",
    description="API for managing products and CSV imports",
    version="1.0.0"
)
app.include_router(webhook.router, prefix="", tags=["Webhooks"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://fulfil-assignment.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for storing uploaded CSV files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

from fastapi import BackgroundTasks

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a CSV file for product import.
    
    The file is saved asynchronously and processing begins in the background.
    Returns a job_id that can be used to poll for import progress.
    
    Args:
        file (UploadFile): The CSV file to upload. Must have .csv extension.
        background_tasks (BackgroundTasks): FastAPI background tasks for async processing.
    
    Returns:
        dict: Contains job_id for tracking the import progress.
        
    Raises:
        HTTPException: 400 if file is not a CSV file.
        
    Example:
        POST /upload
        Content-Type: multipart/form-data
        file: [CSV file]
        
        Response: {"job_id": "uuid-string"}
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")

    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.csv")

    # Save file asynchronously in chunks to handle large files
    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            await out.write(chunk)

    # Initialize job status
    job_status[job_id] = {"status": "processing", "progress": 0, "message": "Parsing CSV"}

    # Run import_csv in background so upload returns immediately
    background_tasks.add_task(import_csv, file_path, job_id)

    return {"job_id": job_id}


@app.get("/job_status/{job_id}")
def get_job_status(job_id: str):
    """
    Get the status of a CSV import job.
    
    Polls the job_status dictionary to return current progress information.
    
    Args:
        job_id (str): The unique identifier of the import job.
    
    Returns:
        dict: Contains status (processing/completed/unknown), progress (0-100), and message.
        
    Example:
        GET /job_status/uuid-string
        
        Response: {
            "status": "processing",
            "progress": 45,
            "message": "Processing row 450 of 1000"
        }
    """
    return job_status.get(
        job_id, {"status": "unknown", "progress": 0, "message": "Job not found"}
    )


@app.get("/products", response_model=List[ProductOut])
def list_products(
    sku: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    List all products with optional filtering and pagination.
    
    Supports case-insensitive partial matching for text fields and
    exact matching for the active status.
    
    Args:
        sku (Optional[str]): Filter by SKU (case-insensitive partial match).
        name (Optional[str]): Filter by product name (case-insensitive partial match).
        description (Optional[str]): Filter by description (case-insensitive partial match).
        active (Optional[bool]): Filter by active status.
        skip (int): Number of records to skip (for pagination). Defaults to 0.
        limit (int): Maximum number of records to return. Defaults to 20.
        db (Session): Database session dependency.
    
    Returns:
        List[ProductOut]: List of products matching the filters.
        
    Example:
        GET /products?sku=prod&active=true&skip=0&limit=10
    """
    query = db.query(Product)
    if sku:
        query = query.filter(Product.sku.ilike(f"%{sku}%"))
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if description:
        query = query.filter(Product.description.ilike(f"%{description}%"))
    if active is not None:
        query = query.filter(Product.active == active)
    return query.offset(skip).limit(limit).all()


# CREATE product
@app.post("/products", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    
    Args:
        product (ProductCreate): Product data to create.
        db (Session): Database session dependency.
    
    Returns:
        ProductOut: The created product with generated ID.
        
    Example:
        POST /products
        {
            "sku": "SKU123",
            "name": "Product Name",
            "description": "Product Description",
            "price": 29.99,
            "active": true
        }
    """
    db_product = Product(
        sku=product.sku,
        sku_lower=product.sku.lower(),
        name=product.name,
        description=product.description,
        price=product.price,
        active=product.active if product.active is not None else True,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# UPDATE product
@app.put("/products/{sku}", response_model=ProductOut)
def update_product(sku: str, product: ProductIn, db: Session = Depends(get_db)):
    """
    Update an existing product by SKU.
    
    Supports partial updates - only provided fields will be updated.
    If SKU is updated, sku_lower is automatically updated as well.
    
    Args:
        sku (str): The SKU of the product to update.
        product (ProductIn): Product data with fields to update.
        db (Session): Database session dependency.
    
    Returns:
        ProductOut: The updated product.
        
    Raises:
        HTTPException: 404 if product with given SKU not found.
        
    Example:
        PUT /products/SKU123
        {
            "name": "Updated Name",
            "price": 39.99
        }
    """
    db_product = db.query(Product).filter(Product.sku == sku).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    data = product.dict(exclude_unset=True)

    # If SKU is being updated, also update sku_lower
    if "sku" in data:
        data["sku_lower"] = data["sku"].lower()

    for key, value in data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


# DELETE product
@app.delete("/products/{sku}")
def delete_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """
    Delete a product by SKU.
    
    Args:
        sku (str): The SKU of the product to delete.
        db (Session): Database session dependency.
    
    Returns:
        dict: Confirmation message.
        
    Raises:
        HTTPException: 404 if product with given SKU not found.
        
    Example:
        DELETE /products/SKU123
    """
    db_product = db.query(Product).filter(Product.sku == sku).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": f"Product with SKU '{sku}' deleted successfully"}


@app.delete("/products")
def delete_all_products(db: Session = Depends(get_db)):
    """
    Delete all products from the database.
    
    WARNING: This operation is irreversible. Use with caution.
    
    Args:
        db (Session): Database session dependency.
    
    Returns:
        dict: Message with count of deleted products.
        
    Raises:
        HTTPException: 500 if deletion fails.
        
    Example:
        DELETE /products
    """
    try:
        deleted_count = db.query(Product).delete(synchronize_session=False)
        db.commit()
        return {"message": f"Deleted {deleted_count} products successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete products: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
