# Project Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Layer (Browser)                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Next.js Frontend (http://localhost:3000)               │  │
│  │  ┌────────────────┐ ┌─────────────┐ ┌──────────────┐    │  │
│  │  │  Upload Page   │ │Products Page│ │ Webhooks Page│   │  │
│  │  │  - CSV Upload  │ │ - CRUD Ops  │ │- Management │    │  │
│  │  │  - Progress    │ │ - Search    │ │- Test Calls │    │  │
│  │  │  - Job Status  │ │ - Filter    │ │- Events     │    │  │
│  │  └────────────────┘ └─────────────┘ └──────────────┘    │  │
│  │                                                          │  │
│  │  Technology: React 18, TypeScript, Tailwind CSS, Axios │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↑                                    │
│                            │ HTTP/REST API                      │
│                            ↓                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    API Layer (Backend)                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ FastAPI Application (http://localhost:8000)             │  │
│  │                                                          │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │ API Endpoints (main.py)                          │   │  │
│  │  │                                                   │   │  │
│  │  │  Products Routes:        Webhooks Routes:        │   │  │
│  │  │  • GET    /products      • GET    /webhooks      │   │  │
│  │  │  • POST   /products      • POST   /webhooks      │   │  │
│  │  │  • PUT    /products/{id} • PUT    /webhooks/{id} │   │  │
│  │  │  • DELETE /products      • DELETE /webhooks/{id} │   │  │
│  │  │                          • POST   /webhooks/test │   │  │
│  │  │  Upload Routes:                                   │   │  │
│  │  │  • POST   /upload                                │   │  │
│  │  │  • GET    /job_status/{job_id}                  │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                            ↓                              │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │ Request Processing Layer                         │   │  │
│  │  │ • Validation (Pydantic schemas.py)              │   │  │
│  │  │ • Business Logic (crud.py, tasks.py)            │   │  │
│  │  │ • Session Management (db.py)                    │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                                                          │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │ CORS Middleware                                  │   │  │
│  │  │ • Allows localhost:3000, vercel.app              │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                                                          │  │
│  │  Technology: Python 3.10+, FastAPI, SQLAlchemy         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↑                                    │
│                            │ SQL Queries                        │
│                            ↓                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 Data Layer (Database)                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PostgreSQL Database (products_db)                        │  │
│  │                                                          │  │
│  │  ┌──────────────────┐         ┌──────────────────┐     │  │
│  │  │ Products Table   │         │ Webhooks Table   │     │  │
│  │  │ • id (PK)        │         │ • id (PK)        │     │  │
│  │  │ • sku (UNIQUE)   │         │ • url            │     │  │
│  │  │ • sku_lower      │         │ • event_types    │     │  │
│  │  │ • name           │         │ • active         │     │  │
│  │  │ • description    │         │ • created_at     │     │  │
│  │  │ • price          │         │ • updated_at     │     │  │
│  │  │ • active         │         └──────────────────┘     │  │
│  │  │ • created_at     │                                  │  │
│  │  │ • updated_at     │         Indices:               │  │
│  │  └──────────────────┘         • uq_sku_lower          │  │
│  │                               • Primary Keys          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Technology: PostgreSQL 12+                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Background Task & Async Layer                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Job Management System                                    │  │
│  │                                                          │  │
│  │  FastAPI BackgroundTasks:                               │  │
│  │  • import_csv(file_path, job_id)                        │  │
│  │    - Reads CSV file                                    │  │
│  │    - Parses product data                               │  │
│  │    - Upserts to database                               │  │
│  │    - Updates job_status dict                           │  │
│  │    - Cleans up file                                    │  │
│  │                                                          │  │
│  │  In-Memory Job Status:                                  │  │
│  │  {job_id: {status, progress, message}}                │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Technology: Python asyncio, FastAPI BackgroundTasks          │  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     File Storage                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ uploads/ directory                                       │  │
│  │ • Temporary CSV files during import                     │  │
│  │ • Deleted after processing                              │  │
│  │                                                          │  │
│  │ Technology: Filesystem                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### CSV Import Flow

```
User selects CSV
       ↓
POST /upload
       ↓
File saved to uploads/
Job created {job_id, status: processing}
       ↓
Response with job_id ← Return to client
       ↓
BackgroundTask: import_csv(file_path, job_id)
       ├─ Read CSV file line-by-line
       ├─ Parse columns (sku, name, price, etc.)
       ├─ Validate data
       ├─ Call upsert_product(db, product)
       │  └─ PostgreSQL INSERT ON CONFLICT UPDATE
       ├─ Update job_status[job_id].progress
       ├─ Batch commit every 500 rows
       └─ Update job_status[job_id].status = "completed"

Meanwhile, Frontend:
       ├─ GET /job_status/{job_id} every 10 seconds
       ├─ Update progress bar
       ├─ Display status message
       └─ Stop polling when status = "completed"

Cleanup:
       ├─ Delete CSV file from uploads/
       └─ Job status kept in memory (can expire)
```

### Product CRUD Flow

```
Frontend Request
       ↓
FastAPI Endpoint (main.py)
       ↓
Pydantic Validation (schemas.py)
       ↓
Database Operation (crud.py / models.py)
       ├─ Query construction
       ├─ SQLAlchemy ORM mapping
       └─ Execute on PostgreSQL
       ↓
Response Serialization
       ↓
Return to Frontend
```

---

## Component Interactions

### Request/Response Cycle

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │ HTTP Request (JSON)
       ↓
┌──────────────────────┐
│ FastAPI Server       │
│ - CORS Middleware    │
│ - Route Handler      │
│ - Request Validation │
└──────┬───────────────┘
       │
       ├─→ Database Layer
       │   └─→ PostgreSQL
       │
       └─→ Response
           (JSON)
       ↓
┌──────────────┐
│   Browser    │
│ - Parse JSON │
│ - Update UI  │
└──────────────┘
```

---

## Technology Stack Summary

### Frontend Stack

```
├─ Runtime: Node.js 18+
├─ Framework: Next.js 14+
├─ UI Library: React 18+
├─ Language: TypeScript
├─ Styling: Tailwind CSS
├─ HTTP Client: Axios
├─ Routing: Next.js App Router
└─ Build Tool: Webpack (via Next.js)
```

### Backend Stack

```
├─ Runtime: Python 3.10+
├─ Framework: FastAPI
├─ Web Server: Uvicorn
├─ ORM: SQLAlchemy 2.0+
├─ Validation: Pydantic v2
├─ Database: PostgreSQL 12+
├─ Async I/O: aiofiles, httpx
└─ Production: Gunicorn/Uvicorn
```

---

## Deployment Architecture

### Local Development

```
Developer Machine
├─ Frontend: npm run dev → http://localhost:3000
├─ Backend: uvicorn → http://localhost:8000
└─ Database: PostgreSQL (localhost:5432)
```

### Production (Railway + Vercel)

```
┌─────────────────────────────────────────────────┐
│           Vercel CDN (Caching Layer)            │
└─────────────┬───────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────┐
│ Vercel (Frontend Hosting)                       │
│ • Next.js App                                   │
│ • Static Files                                  │
│ • Serverless Functions (if needed)              │
└─────────────┬───────────────────────────────────┘
              │ HTTP API Calls
┌─────────────▼───────────────────────────────────┐
│ Railway (Backend Hosting)                       │
│ • FastAPI Application                           │
│ • PostgreSQL Database (Railway managed)         │
└─────────────────────────────────────────────────┘
```

---

## Security Architecture

### CORS Configuration

```
Allowed Origins:
├─ http://localhost:3000 (development)
└─ https://fulfil-assignment.vercel.app (production)

Allowed Methods:
└─ GET, POST, PUT, DELETE, OPTIONS

Allowed Headers:
└─ * (all headers)

Credentials:
└─ true (allow cookies)
```

### Data Validation

```
Request → Pydantic Schema Validation
          ├─ Type checking
          ├─ Required fields
          ├─ Format validation (URLs, decimals)
          └─ Business logic validation
             ↓
          If valid → Process
          If invalid → 400 Bad Request
```

### Database Security

```
PostgreSQL Features:
├─ User authentication (postgres user)
├─ Connection pooling (limit connections)
├─ Prepared statements (prevent SQL injection)
├─ Transaction isolation (ACID)
└─ Encrypted connections (optional)
```

---

## Performance Optimization Points

### Frontend

```
├─ Code Splitting (automatic via Next.js)
├─ Image Optimization (next/image component)
├─ Lazy Loading (dynamic imports)
├─ CSS Minification (Tailwind)
└─ Caching (HTTP cache headers)
```

### Backend

```
├─ Connection Pooling (SQLAlchemy)
│  └─ pool_size=20, max_overflow=40
├─ Query Optimization
│  ├─ Pagination (limit 20 default)
│  ├─ Indexed lookups (sku_lower)
│  └─ Batch operations
├─ Async I/O (aiofiles, httpx)
└─ Compression (gzip)
```

### Database

```
├─ Indices
│  └─ uq_sku_lower (unique constraint)
├─ Connection Pooling
├─ Query Planning
└─ Batch Commits (every 500 rows)
```

---

## Scalability Considerations

### Current Architecture (Single Server)

```
Suitable for:
├─ Development
├─ Small teams
├─ < 1000 products
└─ < 100 concurrent users
```

### Future Scaling Options

```
Horizontal Scaling:
├─ Load Balancer (Nginx, AWS ELB)
├─ Multiple FastAPI instances
├─ Database Replication (master-slave)
Vertical Scaling:
├─ Increase server resources
├─ Database query optimization
├─ Caching layer (Redis)
└─ CDN for static assets
```

---

## Error Handling Flow

```
Request Error
      ↓
Try-Catch Block
      ↓
├─ Validation Error → 400 Bad Request
├─ Not Found → 404 Not Found
├─ Database Error → 500 Internal Server Error
└─ External API Error → 400/500 with detail
      ↓
Return JSON Error Response
      ↓
Frontend
├─ Parse error
├─ Display user-friendly message
└─ Optional: Retry button
```

---

## Monitoring & Logging Points

```
Backend Logging:
├─ API request/response (FastAPI)
├─ Database queries (SQLAlchemy)
├─ CSV import progress (tasks.py)
├─ Webhook calls (webhook.py)
└─ Errors and exceptions

Frontend Logging:
├─ Console logs for debugging
├─ Error boundary catches
└─ API call failures

Database:
├─ Query performance
├─ Connection pool stats
└─ Slow query logs
```

