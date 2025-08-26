from celery import Celery
from app.core.config import settings

# Создаем экземпляр Celery
celery_app = Celery("delivery")

# Конфигурация
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND
celery_app.conf.timezone = "UTC"

# Явно регистрируем задачи
celery_app.conf.task_routes = {
    'app.tasks.jobs.compute_costs': {'queue': 'celery'}
}

# Расписание для beat
celery_app.conf.beat_schedule = {
    "compute-delivery-costs-every-5min": {
        "task": "app.tasks.jobs.compute_costs",
        "schedule": 300.0,  # каждые 5 минут
    }
}