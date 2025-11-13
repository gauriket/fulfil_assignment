"""
Webhook management endpoints and webhook trigger handlers.

This module provides:
- CRUD operations for webhook configurations
- Webhook testing functionality to verify endpoints
- Integration points for sending notifications to external systems

Webhooks allow external systems to receive notifications about events
in the product management system (e.g., product import completion).
"""

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
    """
    Retrieve all configured webhooks.
    
    Returns:
        list[WebhookOut]: List of all webhook configurations.
        
    Example:
        GET /webhooks
        
        Response: [
            {
                "id": 1,
                "url": "https://example.com/webhook",
                "event_types": ["product.imported"],
                "active": true
            }
        ]
    """
    return db.query(Webhook).all()

# Create a webhook
@router.post("/webhooks", response_model=WebhookOut)
def create_webhook(webhook: WebhookCreate, db: Session = Depends(get_db)):
    """
    Create a new webhook configuration.
    
    Args:
        webhook (WebhookCreate): Webhook configuration data.
        db (Session): Database session dependency.
    
    Returns:
        WebhookOut: The created webhook with generated ID.
        
    Example:
        POST /webhooks
        {
            "url": "https://example.com/webhook",
            "event_types": ["product.imported", "product.updated"],
            "active": true
        }
    """
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
    """
    Update an existing webhook configuration.
    
    Supports partial updates - only provided fields will be updated.
    
    Args:
        webhook_id (int): ID of the webhook to update.
        webhook (WebhookUpdate): Fields to update.
        db (Session): Database session dependency.
    
    Returns:
        WebhookOut: The updated webhook.
        
    Raises:
        HTTPException: 404 if webhook not found.
        
    Example:
        PUT /webhooks/1
        {
            "active": false
        }
    """
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
    """
    Delete a webhook configuration.
    
    Args:
        webhook_id (int): ID of the webhook to delete.
        db (Session): Database session dependency.
    
    Returns:
        dict: Confirmation message.
        
    Raises:
        HTTPException: 404 if webhook not found.
        
    Example:
        DELETE /webhooks/1
    """
    db_webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.delete(db_webhook)
    db.commit()
    return {"message": "Webhook deleted successfully."}

# Test webhook (send a test payload)
@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: int, db: Session = Depends(get_db)):
    """
    Send a test payload to a webhook to verify it's working.
    
    This endpoint helps verify that a webhook URL is reachable and accepting requests
    before being used for actual event notifications.
    
    Args:
        webhook_id (int): ID of the webhook to test.
        db (Session): Database session dependency.
    
    Returns:
        dict: Contains:
            - status_code: HTTP response status from the webhook endpoint
            - response_time_ms: Time taken for the webhook to respond
            - response_body: The response body from the webhook
            
    Raises:
        HTTPException: 404 if webhook not found, 400 if request fails.
        
    Example:
        POST /webhooks/1/test
        
        Response: {
            "status_code": 200,
            "response_time_ms": 145.32,
            "response_body": "OK"
        }
    """
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
