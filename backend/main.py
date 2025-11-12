import time
from fastapi import BackgroundTasks, FastAPI, UploadFile, File, HTTPException
import os, uuid, aiofiles
from tasks import import_csv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.csv")
    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024*1024):
            await out.write(chunk)
    import_csv.apply_async(args=[file_path, job_id], queue="imports")
    return {"job_id": job_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )