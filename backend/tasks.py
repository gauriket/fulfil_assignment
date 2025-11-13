"""
Background task handling for CSV import operations.

This module provides:
- CSV file parsing and import into the database
- Real-time progress tracking for import jobs
- Asynchronous processing using in-memory job status tracking

The import_csv function is called as a background task when users upload CSV files.
Progress is tracked via the job_status dictionary and exposed through the API.
"""

import os
import csv
import uuid
from sqlalchemy.orm import Session
from redis import Redis
from db import SessionLocal
from crud import upsert_product
from schemas import ProductCreate

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

# In-memory dictionary to track import job status
# Format: {job_id: {"status": "processing|completed|unknown", "progress": 0-100, "message": "..."}}
job_status = {}


def import_csv(file_path, job_id):
    """
    Import products from a CSV file into the database.
    
    This function:
    1. Reads the CSV file line by line
    2. Parses product data from each row
    3. Upserts products into the database (insert or update if exists)
    4. Tracks progress in real-time
    5. Cleans up the uploaded file when complete
    
    CSV Format Expected:
        - Headers: sku, SKU, name, description, price (case-insensitive)
        - SKU is required; others are optional
        - Empty rows are skipped
    
    Args:
        file_path (str): Absolute path to the CSV file to import.
        job_id (str): Unique identifier for this import job (UUID).
        
    Progress Tracking:
        Updates job_status[job_id] with:
        - status: "processing" while running, "completed" when done
        - progress: 0-100 percentage of rows processed
        - message: Status message for UI display
        
    Raises:
        Exception: On CSV parsing or database errors. Status is set to "unknown".
        
    Cleanup:
        The CSV file is deleted after successful or failed import.
    """
    job_status[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Parsing CSV",
    }
    db: Session = SessionLocal()
    try:
        # Count total rows for progress calculation (excluding header)
        total = sum(1 for _ in open(file_path, encoding="utf-8", errors="ignore")) - 1
        processed = 0

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            processed = 0
            for row in reader:
                # Handle both "sku" and "SKU" header variants
                sku = row.get("sku") or row.get("SKU")
                if not sku or not any(row.values()):
                    continue

                # Parse price as float, handle missing values
                price = float(row.get("price")) if row.get("price") else None
                product = ProductCreate(
                    sku=sku.strip(),
                    name=row.get("name"),
                    description=row.get("description"),
                    price=price,
                    active=True,
                )

                # Upsert product into database
                upsert_product(db, product)
                processed += 1
                
                # Update progress percentage
                job_status[job_id]["progress"] = int((processed / total) * 100)

                # Batch commits for efficiency (every 500 rows)
                if processed % 500 == 0:
                    db.commit()

            # Final commit for remaining rows
            db.commit()

        # Mark job as completed
        job_status[job_id]["status"] = "completed"
        job_status[job_id]["message"] = "Import complete"

    except Exception as e:
        # Reset status on error (unknown will be returned by API if queried)
        job_status[job_id] = {"status": "unknown", "progress": 0, "message": "Job not found"}
        raise
    finally:
        db.close()
        # Clean up the uploaded CSV file
        if os.path.exists(file_path):
            os.remove(file_path)
