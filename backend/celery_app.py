from celery import Celery
import os
import tasks

BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

celery = Celery(
    "worker",
    broker=BROKER,
    backend=BACKEND,
    include=["tasks"],
)

celery.conf.task_routes = {"tasks.import_csv": {"queue": "imports"}}
