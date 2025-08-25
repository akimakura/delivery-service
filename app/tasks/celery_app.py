from celery import Celery
from app.core.config import settings


celery_app = Celery("delivery")
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND
celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "compute-delivery-costs-every-5min": {
        "task": "app.tasks.jobs.compute_costs",
        "schedule": 300.0,  # каждые 5 минут
    }
}