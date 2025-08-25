from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.api import parcels, parcel_types, tasks

app = FastAPI(title="Delivery Service", version="0.1.0")

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET, same_site="lax")

# Подключаем маршруты
app.include_router(parcel_types.router)
app.include_router(parcels.router)
app.include_router(tasks.router)
