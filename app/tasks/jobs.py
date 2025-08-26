from decimal import Decimal, ROUND_HALF_UP
from celery import shared_task
from sqlalchemy import update, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
if bool(os.getenv("PYTEST_CURRENT_TEST")) or os.getenv("TESTING") == "true":
    from app.core.config_test import settings
else:
    from app.core.config import settings
from app.models.parcel import Parcel
import asyncio
from app.services.rates import get_usd_rub_rate


# sync engine для celery, проще жизненный цикл
_db_url = settings.DATABASE_URL
if _db_url.startswith("sqlite+aiosqlite"):
    # Для тестов переключаемся на синхронный sqlite драйвер
    _db_url = _db_url.replace("sqlite+aiosqlite", "sqlite")
else:
    _db_url = _db_url.replace("+aiomysql", "+pymysql")

engine = create_engine(_db_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def _calc(weight_kg: Decimal, content_usd: Decimal, rate: Decimal) -> Decimal:
    cost = (weight_kg * Decimal("0.5") + content_usd * Decimal("0.01")) * rate
    return cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@shared_task(bind=True, name="app.tasks.jobs.compute_costs")
def compute_costs(self):
    # тянем курс (через httpx/redis) — вызываем в asyncio-лупе
    rate = Decimal(str(asyncio.run(get_usd_rub_rate())))
    with SessionLocal() as db:
        rows = db.execute(select(Parcel).where(Parcel.delivery_cost_rub.is_(None))).scalars().all()
        for p in rows:
            p.delivery_cost_rub = _calc(Decimal(p.weight_kg), Decimal(p.content_value_usd), rate)
        db.commit()
    return {"updated": len(rows)}