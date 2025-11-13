import os, csv, uuid
from sqlalchemy.orm import Session
from redis import Redis
from db import SessionLocal
from crud import upsert_product
from schemas import ProductCreate

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

job_status = {}


def import_csv(file_path, job_id):
    job_status[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Parsing CSV",
    }
    db: Session = SessionLocal()
    try:
        total = sum(1 for _ in open(file_path, encoding="utf-8", errors="ignore")) - 1
        processed = 0

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            processed = 0
            for row in reader:
                sku = row.get("sku") or row.get("SKU")
                if not sku or not any(row.values()):
                    continue

                price = float(row.get("price")) if row.get("price") else None
                product = ProductCreate(
                    sku=sku.strip(),
                    name=row.get("name"),
                    description=row.get("description"),
                    price=price,
                    active=True,
                )

                upsert_product(db, product)
                processed += 1
                job_status[job_id]["progress"] = int((processed / total) * 100)

                if processed % 500 == 0:
                    db.commit()

            db.commit()

        job_status[job_id]["status"] = "completed"
        job_status[job_id]["message"] = "Import complete"

    except Exception as e:
        job_status[job_id]={"status": "unknown", "progress": 0, "message": "Job not found"}
        raise
    finally:
        db.close()
        os.remove(file_path)  # optional cleanup
