from fastapi import APIRouter, Depends, Request, Query
from app.db.database import get_session, AsyncSession
from typing import Optional
from app.api.crud import ParcelCRUD, ParcelTypeCRUD
from app.schemas import Envelope, ParcelIn, ParcelOut, Page
from app.core.sessions import get_or_create_session_id
from app.tasks.jobs import compute_costs as compute_costs_task

# Создаем основной роутер
api_router = APIRouter()

# Подроутеры для разных модулей
parcel_types_router = APIRouter(tags=["parcel_types"])
parcels_router = APIRouter(tags=["parcels"])
tasks_router = APIRouter(tags=["tasks"])

# Эндпоинты для типов посылок
@parcel_types_router.get("/parcel-types", response_model=Envelope)
async def get_types(db: AsyncSession = Depends(get_session)):
    """
    Получить список всех типов посылок (справочник).
    Нужен, чтобы фронт/клиент знал, какие type_id можно указывать при создании посылки.
    """
    crud = ParcelTypeCRUD(db)
    types = await crud.get_all_types()
    return {"success": True, "data": types}

# Эндпоинты для посылок
@parcels_router.post("/parcels/register", response_model=Envelope)
async def register_parcel(
    parcel: ParcelIn, 
    request: Request, 
    db: AsyncSession = Depends(get_session)
):
    """
    Зарегистрировать новую посылку.
    Выдаёт уникальный id в рамках сессии (session_seq).
    """
    sid = get_or_create_session_id(request)
    crud = ParcelCRUD(db)
    
    last_seq = await crud.get_last_sequence(sid)
    new_parcel = await crud.create_parcel(parcel, sid, last_seq + 1)
    
    return {"success": True, "data": {"id": new_parcel.session_seq}}

@parcels_router.get("/parcels", response_model=Envelope)
async def list_parcels(
    request: Request,
    db: AsyncSession = Depends(get_session),
    type_id: Optional[int] = Query(None),
    has_cost: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Получить список посылок текущего пользователя (по session_id).
    Можно фильтровать по типу посылки и по наличию стоимости доставки.
    Поддерживает пагинацию.
    """
    sid = get_or_create_session_id(request)
    crud = ParcelCRUD(db)
    
    total, rows = await crud.get_parcels_with_types(
        session_id=sid,
        type_id=type_id,
        has_cost=has_cost,
        limit=limit,
        offset=offset
    )
    
    items = [crud.format_parcel_output(parcel, ptype) for parcel, ptype in rows]
    return {"success": True, "data": Page(total=total, items=items).model_dump()}

@parcels_router.get("/parcels/{parcel_id}", response_model=Envelope)
async def get_parcel(
    parcel_id: int, 
    request: Request, 
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о конкретной посылке.
    Выдаёт информацию о посылке, если она принадлежит текущему пользователю.
    """
    sid = get_or_create_session_id(request)
    crud = ParcelCRUD(db)
    
    result = await crud.get_parcel_with_type(sid, parcel_id)
    if not result:
        return {"success": False, "error": {"code": "not_found", "detail": "Посылка не найдена"}}
    
    parcel, ptype = result
    return {"success": True, "data": crud.format_parcel_output(parcel, ptype).model_dump()}

# Эндпоинты для задач
@tasks_router.post("/tasks/compute-costs", response_model=Envelope)
def manual_compute():
    """
    Ручной запуск пересчёта стоимости доставки.
    """
    res = compute_costs_task.delay()
    return {"success": True, "data": {"task_id": res.id}}

# Подключаем все роутеры к основному
api_router.include_router(parcel_types_router)
api_router.include_router(parcels_router)
api_router.include_router(tasks_router)
