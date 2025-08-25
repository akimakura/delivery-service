from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy import select, func
from app.db.database import get_session, AsyncSession
from app.models.parcel import Parcel
from app.models.parcel_type import ParcelType
from app.schemas import Envelope, ParcelIn, ParcelOut, Page
from app.core.sessions import get_or_create_session_id


router = APIRouter(tags=["parcels"])

@router.post("/parcels/register", response_model=Envelope)
async def register(parcel: ParcelIn, request: Request, db: AsyncSession = Depends(get_session)):
    sid = get_or_create_session_id(request)
    last_seq = (await db.execute(
        select(func.coalesce(func.max(Parcel.session_seq), 0)).where(Parcel.session_id == sid)
    )).scalar_one()
    p = Parcel(
        session_id=sid,
        session_seq=last_seq + 1,
        title=parcel.title,
        weight_kg=parcel.weight_kg,
        content_value_usd=parcel.content_value_usd,
        type_id=parcel.type_id,
    )
    db.add(p)
    await db.commit()
    return {"success": True, "data": {"id": p.session_seq}}

@router.get("/parcels", response_model=Envelope)
async def list_parcels(
    request: Request,
    db: AsyncSession = Depends(get_session),
    type_id: int | None = Query(None),
    has_cost: bool | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    sid = get_or_create_session_id(request)
    q = select(Parcel, ParcelType).join(ParcelType).where(Parcel.session_id == sid)
    if type_id is not None:
        q = q.where(Parcel.type_id == type_id)
    if has_cost is not None:
        q = q.where((Parcel.delivery_cost_rub.is_not(None)) if has_cost else (Parcel.delivery_cost_rub.is_(None)))

    total = (await db.execute(q.with_only_columns(func.count()))).scalar()
    rows = (await db.execute(q.order_by(Parcel.id).limit(limit).offset(offset))).all()

    items = [
        ParcelOut(
            id=parcel.session_seq,
            title=parcel.title,
            weight_kg=float(parcel.weight_kg),
            type_name=ptype.name,
            content_value_usd=float(parcel.content_value_usd),
            delivery_cost_rub=(float(parcel.delivery_cost_rub) if parcel.delivery_cost_rub else "Не рассчитано"),
        )
        for parcel, ptype in rows
    ]
    return {"success": True, "data": Page(total=total, items=items).model_dump()}

@router.get("/parcels/{parcel_id}", response_model=Envelope)
async def get_parcel(parcel_id: int, request: Request, db: AsyncSession = Depends(get_session)):
    sid = get_or_create_session_id(request)
    row = (await db.execute(
        select(Parcel, ParcelType)
        .join(ParcelType)
        .where(Parcel.session_id == sid, Parcel.session_seq == parcel_id)
    )).first()
    if not row:
        return {"success": False, "error": {"code": "not_found", "detail": "Посылка не найдена"}}

    parcel, ptype = row
    return {"success": True, "data": ParcelOut(
        id=parcel.session_seq,
        title=parcel.title,
        weight_kg=float(parcel.weight_kg),
        type_name=ptype.name,
        content_value_usd=float(parcel.content_value_usd),
        delivery_cost_rub=(float(parcel.delivery_cost_rub) if parcel.delivery_cost_rub else "Не рассчитано"),
    ).model_dump()}
