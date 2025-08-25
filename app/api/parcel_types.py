from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.db.database import get_session, AsyncSession
from app.models.parcel_type import ParcelType
from app.schemas import ParcelTypeOut, Envelope


router = APIRouter(tags=["parcel_types"])

@router.get("/parcel-types", response_model=Envelope)
async def get_types(db: AsyncSession = Depends(get_session)):
    rows = (await db.execute(select(ParcelType))).scalars().all()
    return {"success": True, "data": [ParcelTypeOut(id=t.id, name=t.name) for t in rows]}