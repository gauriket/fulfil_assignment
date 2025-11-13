from typing import List, Optional
from fastapi import BackgroundTasks, Depends, FastAPI, UploadFile, File, HTTPException
import os, uuid, aiofiles
from models import Product
from db import get_db
from schemas import ProductCreate, ProductIn, ProductOut
from tasks import import_csv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.csv")
    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            await out.write(chunk)
    import_csv(file_path, job_id)
    return {"job_id": job_id}


@app.get("/products", response_model=List[ProductOut])
def list_products(
    sku: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),  # ✅ THIS FIXES IT
):
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
    db_product = db.query(Product).filter(Product.sku == sku).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": f"Product with SKU '{sku}' deleted successfully"}


@app.delete("/products")
def delete_all_products(db: Session = Depends(get_db)):
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
