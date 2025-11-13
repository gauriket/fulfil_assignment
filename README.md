# Fulfil Assignment - CSV Product Uploader

A full-stack application for managing products with CSV import capabilities, real-time progress tracking, and webhook notifications.

**Status:** ✅ Production Ready  
**Last Updated:** November 13, 2025

---

## Overview

This project provides a comprehensive product management system with:

- 📤 **CSV Upload** with real-time progress tracking
- 🔍 **Product Management** (CRUD operations with search/filter)
- 🪝 **Webhook Integration** for event notifications
- 📊 **Real-time Status Updates** via job polling
- 🛡️ **Data Validation** with Pydantic
- 🚀 **Production Ready** deployment to Railway + Vercel

---

## Quick Links

### Documentation

| Document | Purpose |
|----------|---------|
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete API reference with examples |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and data flow diagrams |
| [BACKEND_SETUP.md](BACKEND_SETUP.md) | Backend installation and configuration |
| [FRONTEND_SETUP.md](FRONTEND_SETUP.md) | Frontend installation and configuration |

### Live Demo

- **Frontend:** [https://fulfil-assignment.vercel.app](https://fulfil-assignment.vercel.app)
- **Backend API:** [https://fulfilassignment-production.up.railway.app](https://fulfilassignment-production.up.railway.app)
- **API Docs:** [https://fulfilassignment-production.up.railway.app/docs](https://fulfilassignment-production.up.railway.app/docs)

---

## Features

### Core Features

✨ **CSV Import**
- Batch upload products via CSV file
- Real-time progress tracking (0-100%)
- Automatic file validation and cleanup
- Error handling with retry functionality

🎯 **Product Management**
- Create, read, update, and delete products
- Advanced search by SKU, name, description
- Filter by active status
- Pagination support (default 20 items)

🪝 **Webhook Management**
- Configure webhook endpoints
- Subscribe to event types
- Test webhook connectivity
- Enable/disable webhooks

📱 **User Interface**
- Responsive design with Tailwind CSS
- Real-time progress visualization
- Status messages and error feedback
- Navigation between different pages

---

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL 12+
- **ORM:** SQLAlchemy 2.0+
- **Validation:** Pydantic v2
- **Server:** Uvicorn
- **Async:** aiofiles, httpx

### Frontend
- **Framework:** Next.js 14+
- **Language:** TypeScript
- **UI Library:** React 18+
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Deployment:** Vercel

### Infrastructure
- **Backend Hosting:** Railway
- **Database:** Railway PostgreSQL
- **Frontend Hosting:** Vercel
- **Storage:** Filesystem (uploads/)

---

## Architecture at a Glance

```
┌─────────────────┐
│  Browser        │
│  (Next.js App)  │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│  FastAPI        │
│  + PostgreSQL   │
└─────────────────┘

Full architecture: See ARCHITECTURE.md
```

---

## Getting Started

### Prerequisites

* Node.js >= 18
* Python >= 3.10
* PostgreSQL (for local development)
* Railway account (for backend deployment)
* Vercel account (for frontend deployment)

---

## Environment Variables

### Backend (.env)

```env
# Required
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/products_db

```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (Railway/Vercel)

Set environment variables in respective dashboards.

---

## Backend Setup (FastAPI)

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Run locally**

```bash
uvicorn main:app --reload
```

3. **Database Setup**

```python
from models import Base
from database import engine

Base.metadata.create_all(bind=engine)
```

4. **Environment Configuration**

* Ensure `DATABASE_URL` points to your PostgreSQL instance.
* On Railway, set `DATABASE_URL` in project settings.

5. **CORS Configuration**

Allow requests from frontend URL:

```python
from fastapi.middleware.cors import CORSMiddleware

origins = ["https://fulfil-assignment.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Frontend Setup (Next.js)

1. **Install dependencies**

```bash
npm install
# or
yarn
```

2. **Environment Variables**

* Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://fulfilassignment-production.up.railway.app
```

3. **Run locally**

```bash
npm run dev
# or
yarn dev
```

4. **Build for production**

```bash
npm run build
npm run start
```

5. **Deploy to Vercel**

* Link your GitHub repository to Vercel
* Add `NEXT_PUBLIC_API_URL` environment variable in Vercel dashboard
* Deploy

---

## Usage

1. Open the frontend URL
2. Select a CSV file
3. Click **Upload**
4. Watch the **progress bar** and status updates
5. If an error occurs, click **Retry**

**CSV Format Example:**

| sku   | name      | description | price |
| ----- | --------- | ----------- | ----- |
| 12345 | Product A | Example     | 12.5  |
| 67890 | Product B | Example     | 9.99  |

---

## Deployment Notes

* **Backend:** Railway automatically exposes a public URL. Use that URL in `NEXT_PUBLIC_API_URL`.
* **Frontend:** Vercel fetches from the backend URL. Ensure CORS is configured correctly.
* **Database:** Ensure Railway PostgreSQL is running and `DATABASE_URL` points to it.

---

## Project Structure

```
fulfil_assignment/
├── backend/                  # FastAPI backend
│   ├── main.py              # API endpoints
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── db.py                # Database setup
│   ├── tasks.py             # CSV import task
│   ├── webhook.py           # Webhook endpoints
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js frontend
│   ├── app/
│   │   ├── page.tsx         # Upload page
│   │   ├── products/        # Products page
│   │   ├── webhooks/        # Webhooks page
│   │   └── layout.tsx       # Root layout
│   ├── package.json         # Node dependencies
│   └── tsconfig.json        # TypeScript config
├── uploads/                  # Temporary CSV files
├── API_DOCUMENTATION.md      # Full API reference
├── ARCHITECTURE.md           # System design
├── BACKEND_SETUP.md          # Backend setup
└── FRONTEND_SETUP.md         # Frontend setup
```

---

## Troubleshooting

### Common Issues

**CORS Error**
- Add your frontend URL to `allow_origins` in `main.py`
- Restart backend server

**Cannot Connect to Database**
- Ensure PostgreSQL is running
- Check `DATABASE_URL` is correct
- Test connection: `psql postgresql://...`

**Port Already in Use**
- Kill process: `lsof -i :8000` or `netstat -ano | findstr :8000`
- Use different port: `uvicorn main:app --port 8001`

**Build Failed**
- Clear cache: `rm -rf .next node_modules`
- Reinstall: `npm install && npm run build`


---

## Deployment

### Deploy to Railway (Backend)

1. Connect GitHub repository to Railway
2. Set `DATABASE_URL` environment variable
3. Railway auto-deploys on push

### Deploy to Vercel (Frontend)

1. Connect GitHub repository to Vercel
2. Set `NEXT_PUBLIC_API_URL` environment variable
3. Vercel auto-deploys on push

---

## Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and diagrams
- **[BACKEND_SETUP.md](BACKEND_SETUP.md)** - Detailed backend setup
- **[FRONTEND_SETUP.md](FRONTEND_SETUP.md)** - Detailed frontend setup

---

## License

MIT License
