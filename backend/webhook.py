from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Webhook
from schemas import WebhookCreate, WebhookUpdate, WebhookOut
import httpx

router = APIRouter()

# List all webhooks
@router.get("/webhooks", response_model=list[WebhookOut])
def list_webhooks(db: Session = Depends(get_db)):
    return db.query(Webhook).all()

# Create a webhook
@router.post("/webhooks", response_model=WebhookOut)
def create_webhook(webhook: WebhookCreate, db: Session = Depends(get_db)):
    data = webhook.dict()
    data["url"] = str(data["url"])  # Convert HttpUrl to string
    db_webhook = Webhook(**data)
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


# Update a webhook
@router.put("/webhooks/{webhook_id}", response_model=WebhookOut)
def update_webhook(webhook_id: int, webhook: WebhookUpdate, db: Session = Depends(get_db)):
    db_webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    for key, value in webhook.dict(exclude_unset=True).items():
        if key == "url":
            value = str(value)  # convert HttpUrl to string
        setattr(db_webhook, key, value)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


# Delete a webhook
@router.delete("/webhooks/{webhook_id}")
def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    db_webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.delete(db_webhook)
    db.commit()
    return {"message": "Webhook deleted successfully."}

# Test webhook (send a test payload)
@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: int, db: Session = Depends(get_db)):
    db_webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    test_payload = {"message": "Test webhook trigger"}
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(db_webhook.url, json=test_payload)
            return {
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "response_body": response.text,
            }
        except httpx.RequestError as e:
            raise HTTPException(status_code=400, detail=f"Request failed: {str(e)}")
