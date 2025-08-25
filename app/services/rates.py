import json, math
import httpx
from redis import Redis
from app.core.config import settings


redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_usd_rub_rate() -> float:
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