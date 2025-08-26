import json, math
import httpx
from redis import Redis
import os
if bool(os.getenv("PYTEST_CURRENT_TEST")) or os.getenv("TESTING") == "true":
    from app.core.config_test import settings
else:
    from app.core.config import settings


redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_usd_rub_rate() -> float:
    """
    Получаем курс доллара к рублю из Redis или из CBR.
    """
    key = "exrate:usd_rub"
    cached = redis.get(key)
    if cached:
        return float(cached)
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(settings.CBR_URL)
        resp.raise_for_status()
        data = resp.json()
        rate = float(data["Valute"]["USD"]["Value"])
    redis.setex(key, settings.EXRATE_TTL_SECONDS, rate)
    return rate