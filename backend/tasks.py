import os, csv, uuid
from celery import Celery
from sqlalchemy.orm import Session
from redis import Redis
from db import SessionLocal
from crud import upsert_product
from schemas import ProductCreate

BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery("tasks", broker=BROKER, backend=BACKEND)
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

@celery.task(bind=True)
def import_csv(self, file_path, job_id):
    db: Session = SessionLocal()
    try:
        total = sum(1 for _ in open(file_path, encoding="utf-8", errors="ignore")) - 1
        processed = 0
        redis_client.hset(f"import:{job_id}", mapping={"status": "Parsing CSV", "processed": 0, "total": total})

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            with db.begin():  # ensures transaction safety
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
                        active=True
                    )

                    upsert_product(db, product)
                    processed += 1

                    if processed % 500 == 0:
                        db.commit()
                        redis_client.hset(
                            f"import:{job_id}", mapping={"processed": processed, "status": "Processing"}
                        )

        db.commit()
        redis_client.hset(f"import:{job_id}", mapping={"status": "Import Complete", "processed": processed})

    except Exception as e:
        redis_client.hset(f"import:{job_id}", mapping={"status": "Failed", "error": str(e)})
        raise
    finally:
        db.close()
        os.remove(file_path)  # optional cleanup
