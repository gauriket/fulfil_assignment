# Backend Setup & Configuration Guide

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip (Python package manager)

### Installation & Running

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create .env file in backend/ directory
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/products_db
REDIS_URL=redis://localhost:6379/0
EOF

# Run the application
uvicorn main:app --reload

# API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

---

## Database Setup

### PostgreSQL Installation

#### Windows
1. Download from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer
3. Remember the password for `postgres` user
4. PostgreSQL will run on default port 5432

#### macOS
```bash
# Using Homebrew
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql prompt:
CREATE DATABASE products_db;
CREATE USER products_user WITH PASSWORD 'your_password';
ALTER ROLE products_user SET client_encoding TO 'utf8';
ALTER ROLE products_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE products_user SET default_transaction_deferrable TO on;
ALTER ROLE products_user SET default_transaction_read_committed TO on;
GRANT ALL PRIVILEGES ON DATABASE products_db TO products_user;
\q
```

### Update Connection String

Update `.env` file:
```env
DATABASE_URL=postgresql://products_user:your_password@localhost:5432/products_db
```

### Verify Connection

```bash
python -c "from db import engine; print('Connected!' if engine.connect() else 'Failed')"
```

---

### Installation

#### Windows
1. Download from [redis.io](https://redis.io/download) (requires WSL2) or use [memurai](https://www.memurai.com/)
2. Or use Docker

#### macOS
```bash
brew install redis
brew services start redis
```

#### Linux
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

#### Docker (All Platforms)
```bash
docker run -d -p 6379:6379 redis:latest
```

### Verify Installation

```bash
redis-cli ping
# Should return: PONG
```

---

## Dependencies Explanation

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.121.1 | Web framework |
| uvicorn | 0.38.0 | ASGI server |
| sqlalchemy | 2.0.44 | ORM |
| psycopg2-binary | 2.9.11 | PostgreSQL adapter |
| pydantic | 2.12.4 | Data validation |
| httpx | 0.28.1 | Async HTTP client |
| aiofiles | 25.1.0 | Async file I/O |

### Optional Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| redis | Message broker/cache | No (optional) |
| python-dotenv | Environment variables | Optional |

---

## Configuration Details

### Database URL Format

```
postgresql://[user]:[password]@[host]:[port]/[database]

Examples:
- postgresql://postgres:postgres@localhost:5432/products_db
- postgresql://user:pass@db.railway.app:5432/products_db
```

### Environment Variables

#### Required
- `DATABASE_URL`: PostgreSQL connection string

### Creating .env File

```bash
# Create file
touch .env

# Add variables (on Windows, use a text editor)
```

Content:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/products_db
```

---

## CORS Configuration

CORS is configured in `main.py` to allow requests from:

- `http://localhost:3000` (local development)
- `https://fulfil-assignment.vercel.app` (production)

To add more origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://fulfil-assignment.vercel.app",
        "https://your-frontend-url",  # Add here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

---

## Running in Production

### Using Gunicorn + Uvicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t product-api .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  product-api
```

### Using Railway

1. Create `Procfile`:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Set environment variables in Railway dashboard:
   - `DATABASE_URL`

3. Deploy from GitHub

---

## Troubleshooting

### Cannot Connect to Database

**Error:**
```
sqlalchemy.exc.OperationalError: could not translate host name "localhost"
```

**Solutions:**

1. Check PostgreSQL is running:
   ```bash
   psql -U postgres
   ```

2. Verify connection string:
   ```bash
   python -c "from db import DATABASE_URL; print(DATABASE_URL)"
   ```

3. Test connection:
   ```bash
   psql postgresql://postgres:postgres@localhost:5432/products_db
   ```

### Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**

Use different port:
```bash
uvicorn main:app --reload --port 8001
```

Or find and kill process:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### CORS Errors in Frontend

**Error:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**

1. Check that frontend URL is in `allow_origins`
2. Ensure correct API URL in frontend `.env.local`
3. Restart backend server after changing CORS config

### Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**

1. Check virtual environment is activated
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Redis Connection Error

**Error:**
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

**Solution:**

1. Check if Redis is running
2. Start Redis:
   ```bash
   redis-server
   ```
3. Or comment out Redis-dependent code if not needed

---

## Development Workflows

### Running with Auto-Reload

```bash
uvicorn main:app --reload

# Auto-reload on file changes
# Good for development
```

### Running Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_products.py

# Run with coverage
pytest --cov=. tests/
```

### Creating Database Migrations

For production, use Alembic:

```bash
# Install alembic
pip install alembic

# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head
```

---

## Performance Tuning

### Connection Pooling

Already configured in `db.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Validates connections before use
    pool_size=20,        # Number of connections to keep in pool
    max_overflow=40      # Maximum overflow connections
)
```

### Query Optimization

Use pagination for list endpoints:

```python
@app.get("/products")
def list_products(
    skip: int = 0,
    limit: int = 20,  # Limit default results
    db: Session = Depends(get_db)
):
    return db.query(Product).offset(skip).limit(limit).all()
```

### CSV Import Optimization

Batch commits in `tasks.py`:

```python
if processed % 500 == 0:  # Commit every 500 rows
    db.commit()
```

---

## Monitoring & Logging

### Enable FastAPI Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/products")
def list_products(db: Session = Depends(get_db)):
    logger.info("Fetching products")
    return db.query(Product).all()
```

### Monitor Database Queries

```python
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    print(f"Query: {statement}")
    print(f"Params: {params}")
```

---

## Deployment Checklist

- [ ] Database URL configured
- [ ] All environment variables set
- [ ] CORS origins updated for production URL
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database tables created
- [ ] API tested with `uvicorn main:app --reload`
- [ ] FastAPI docs accessible at `/docs`
- [ ] Frontend can reach API
- [ ] HTTPS enabled in production
- [ ] Error logs monitored

---

## Additional Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Pydantic Validation](https://docs.pydantic.dev/)

