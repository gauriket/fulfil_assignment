# Fulfil Assignment - CSV Product Uploader

This project provides a **CSV uploader** for products with real-time progress feedback.
It consists of:

* **Backend:** FastAPI + PostgreSQL (hosted on Railway)
* **Frontend:** Next.js + Tailwind CSS (hosted on Vercel)
* **Features:** Upload CSV, live progress bar, job status polling, retry on error.

---

## Live Demo

* Frontend: [https://fulfil-assignment.vercel.app](https://fulfil-assignment.vercel.app)
* Backend API: [https://fulfilassignment-production.up.railway.app](https://fulfilassignment-production.up.railway.app)

---

## Features

* Real-time upload progress (0–50% for file upload, 50–100% for CSV processing)
* Polling for CSV processing progress
* Error handling with retry option
* Visual feedback with progress bar and status messages

---

## Prerequisites

* Node.js >= 18
* Python >= 3.10
* PostgreSQL (for local development)
* Railway account (for backend deployment)
* Vercel account (for frontend deployment)

---

## Environment Variables

### Backend (`.env` or Railway environment variables)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/products_db
```

> **Important:** On Railway, replace `localhost` with the Railway PostgreSQL connection string.

### Frontend (`.env.local` for Vercel / local development)

```env
NEXT_PUBLIC_API_URL=https://fulfilassignment-production.up.railway.app
```

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

## Troubleshooting

* **Connection Refused / OperationalError:** Check that `DATABASE_URL` is correct and database is accessible.
* **CORS errors:** Make sure the frontend URL is in the FastAPI `allow_origins`.
* **Progress bar jumps / incorrect:** Ensure frontend polls `/job_status/{job_id}` and scales upload vs processing progress correctly.

---

## Tech Stack

* **Backend:** FastAPI, SQLAlchemy, PostgreSQL
* **Frontend:** Next.js, TypeScript, Tailwind CSS, Axios
* **Deployment:** Railway (backend), Vercel (frontend)

---

## License

MIT License
