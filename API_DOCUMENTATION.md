# Product Management API - Documentation

## Overview

This API provides comprehensive product management and CSV import functionality with real-time progress tracking. Built with FastAPI and PostgreSQL, it supports:

- **CSV Product Import** with real-time progress monitoring
- **Product CRUD Operations** (Create, Read, Update, Delete)
- **Webhook Management** for event notifications
- **Advanced Search and Filtering** capabilities

---

## Table of Contents

1. [Base URL](#base-url)
2. [Authentication](#authentication)
3. [Product Endpoints](#product-endpoints)
4. [CSV Upload Endpoints](#csv-upload-endpoints)
5. [Webhook Endpoints](#webhook-endpoints)
6. [Response Formats](#response-formats)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

---

## Base URL

**Production:** `https://fulfilassignment-production.up.railway.app`  
**Local Development:** `http://localhost:8000`

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

---

## Product Endpoints

### List Products

**GET** `/products`

Retrieve all products with optional filtering and pagination.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sku` | string | No | Filter by SKU (case-insensitive partial match) |
| `name` | string | No | Filter by name (case-insensitive partial match) |
| `description` | string | No | Filter by description (case-insensitive partial match) |
| `active` | boolean | No | Filter by active status (true/false) |
| `skip` | integer | No | Number of records to skip (default: 0) |
| `limit` | integer | No | Maximum records to return (default: 20) |

#### Response

**Status:** 200 OK

```json
[
  {
    "sku": "PROD001",
    "name": "Product Name",
    "description": "Product description",
    "price": 29.99,
    "active": true
  },
  {
    "sku": "PROD002",
    "name": "Another Product",
    "description": "Another description",
    "price": 49.99,
    "active": true
  }
]
```

#### Examples

```bash
# Get first 10 products
GET /products?limit=10

# Search by SKU
GET /products?sku=PROD&limit=20

# Filter by active status
GET /products?active=true&limit=50

# Combine filters with pagination
GET /products?name=Phone&active=true&skip=0&limit=10
```

---

### Create Product

**POST** `/products`

Create a new product.

#### Request Body

```json
{
  "sku": "PROD003",
  "name": "New Product",
  "description": "Product description",
  "price": 99.99,
  "active": true
}
```

#### Response

**Status:** 200 OK

```json
{
  "sku": "PROD003",
  "name": "New Product",
  "description": "Product description",
  "price": 99.99,
  "active": true
}
```

---

### Update Product

**PUT** `/products/{sku}`

Update an existing product by SKU. Supports partial updates.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sku` | string | Yes | The SKU of the product to update |

#### Request Body (all fields optional)

```json
{
  "sku": "PROD003_NEW",
  "name": "Updated Product Name",
  "description": "Updated description",
  "price": 109.99,
  "active": false
}
```

#### Response

**Status:** 200 OK

```json
{
  "sku": "PROD003_NEW",
  "name": "Updated Product Name",
  "description": "Updated description",
  "price": 109.99,
  "active": false
}
```

#### Errors

- **404 Not Found:** Product with given SKU not found

---

### Delete Product

**DELETE** `/products/{sku}`

Delete a single product by SKU.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sku` | string | Yes | The SKU of the product to delete |

#### Response

**Status:** 200 OK

```json
{
  "detail": "Product with SKU 'PROD003' deleted successfully"
}
```

#### Errors

- **404 Not Found:** Product with given SKU not found

---

### Delete All Products

**DELETE** `/products`

Delete all products from the database. **WARNING: This operation is irreversible.**

#### Response

**Status:** 200 OK

```json
{
  "message": "Deleted 150 products successfully."
}
```

#### Errors

- **500 Internal Server Error:** Database operation failed

---

## CSV Upload Endpoints

### Upload CSV

**POST** `/upload`

Upload a CSV file for batch product import. Returns immediately with a job ID for progress tracking.

#### Request Body

```
Content-Type: multipart/form-data

file: [CSV file]
```

#### CSV Format

The CSV file should contain the following columns:

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| sku or SKU | string | Yes | Product identifier (case-insensitive, unique) |
| name | string | No | Product name |
| description | string | No | Product description |
| price | float | No | Product price |

#### Example CSV

```csv
sku,name,description,price
PROD001,Laptop,High-performance laptop,999.99
PROD002,Mouse,Wireless mouse,29.99
PROD003,Keyboard,Mechanical keyboard,79.99
```

#### Response

**Status:** 200 OK

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Errors

- **400 Bad Request:** File is not a CSV file

---

### Get Job Status

**GET** `/job_status/{job_id}`

Poll the status of a CSV import job.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | string | Yes | The job ID returned from /upload |

#### Response

**Status:** 200 OK

```json
{
  "status": "processing",
  "progress": 45,
  "message": "Processing row 450 of 1000"
}
```

#### Status Values

- `processing`: Import is in progress
- `completed`: Import finished successfully
- `unknown`: Job not found or error occurred

#### Response Example - Completed

```json
{
  "status": "completed",
  "progress": 100,
  "message": "Import complete"
}
```

---

## Webhook Endpoints

### List Webhooks

**GET** `/webhooks`

Retrieve all configured webhooks.

#### Response

**Status:** 200 OK

```json
[
  {
    "id": 1,
    "url": "https://example.com/webhook",
    "event_types": ["product.imported", "product.updated"],
    "active": true
  }
]
```

---

### Create Webhook

**POST** `/webhooks`

Create a new webhook configuration.

#### Request Body

```json
{
  "url": "https://example.com/webhook",
  "event_types": ["product.imported", "product.updated"],
  "active": true
}
```

#### Response

**Status:** 200 OK

```json
{
  "id": 1,
  "url": "https://example.com/webhook",
  "event_types": ["product.imported", "product.updated"],
  "active": true
}
```

---

### Update Webhook

**PUT** `/webhooks/{webhook_id}`

Update an existing webhook. Supports partial updates.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `webhook_id` | integer | Yes | The ID of the webhook to update |

#### Request Body (all fields optional)

```json
{
  "active": false
}
```

#### Response

**Status:** 200 OK

```json
{
  "id": 1,
  "url": "https://example.com/webhook",
  "event_types": ["product.imported"],
  "active": false
}
```

#### Errors

- **404 Not Found:** Webhook with given ID not found

---

### Delete Webhook

**DELETE** `/webhooks/{webhook_id}`

Delete a webhook configuration.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `webhook_id` | integer | Yes | The ID of the webhook to delete |

#### Response

**Status:** 200 OK

```json
{
  "message": "Webhook deleted successfully."
}
```

#### Errors

- **404 Not Found:** Webhook with given ID not found

---

### Test Webhook

**POST** `/webhooks/{webhook_id}/test`

Send a test payload to a webhook endpoint to verify it's working.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `webhook_id` | integer | Yes | The ID of the webhook to test |

#### Response

**Status:** 200 OK

```json
{
  "status_code": 200,
  "response_time_ms": 145.32,
  "response_body": "OK"
}
```

#### Errors

- **404 Not Found:** Webhook not found
- **400 Bad Request:** Request to webhook endpoint failed

---

## Response Formats

### Success Response

All successful responses return the requested data with HTTP status 200 OK.

```json
{
  "sku": "PROD001",
  "name": "Product Name",
  "description": "Description",
  "price": 29.99,
  "active": true
}
```

### Error Response

Error responses include a detail message.

```json
{
  "detail": "Product not found"
}
```

### HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad Request (e.g., invalid file format) |
| 404 | Not Found (e.g., product doesn't exist) |
| 500 | Internal Server Error |

---

## Error Handling

### Common Errors

#### Product Not Found (404)
```json
{
  "detail": "Product not found"
}
```

#### Invalid CSV File (400)
```json
{
  "detail": "Only CSV allowed"
}
```

#### Webhook Request Failed (400)
```json
{
  "detail": "Request failed: Connection timeout"
}
```

#### Database Error (500)
```json
{
  "detail": "Failed to delete products: Database constraint violation"
}
```

---

## Examples

### Example 1: Complete CSV Import Workflow

```bash
# 1. Upload CSV file
curl -X POST http://localhost:8000/upload \
  -F "file=@products.csv"

# Response:
# {"job_id": "550e8400-e29b-41d4-a716-446655440000"}

# 2. Poll job status
curl http://localhost:8000/job_status/550e8400-e29b-41d4-a716-446655440000

# Response (while processing):
# {"status": "processing", "progress": 50, "message": "Processing rows..."}

# Response (completed):
# {"status": "completed", "progress": 100, "message": "Import complete"}

# 3. List imported products
curl http://localhost:8000/products?limit=50
```

### Example 2: Product Management

```bash
# Create a product
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"sku": "PHONE001", "name": "iPhone", "price": 999.99}'

# Update the product
curl -X PUT http://localhost:8000/products/PHONE001 \
  -H "Content-Type: application/json" \
  -d '{"price": 899.99, "active": true}'

# Get product
curl http://localhost:8000/products?sku=PHONE001

# Delete product
curl -X DELETE http://localhost:8000/products/PHONE001
```

### Example 3: Webhook Setup and Testing

```bash
# Create webhook
curl -X POST http://localhost:8000/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "event_types": ["product.imported"],
    "active": true
  }'

# Test webhook
curl -X POST http://localhost:8000/webhooks/1/test

# Update webhook
curl -X PUT http://localhost:8000/webhooks/1 \
  -H "Content-Type: application/json" \
  -d '{"active": false}'

# Delete webhook
curl -X DELETE http://localhost:8000/webhooks/1
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. All endpoints can be called freely.

---

## Changelog

### Version 1.0.0 (Current)
- Initial release with product CRUD operations
- CSV import with progress tracking
- Webhook management
- Real-time job status polling

