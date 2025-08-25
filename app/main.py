from fastapi import FastAPI
from app.api.routers import api_router

app = FastAPI(title="Delivery Service", version="0.1.0")

# Подключаем все маршруты через единый роутер
app.include_router(api_router)
