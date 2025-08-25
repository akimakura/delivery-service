from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parcel import Parcel
from app.models.parcel_type import ParcelType
from app.schemas import ParcelIn, ParcelOut, Page
from typing import List, Tuple, Optional
from decimal import Decimal


class ParcelCRUD:
    """CRUD операции для посылок"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_parcel(self, parcel_data: ParcelIn, session_id: str, session_seq: int) -> Parcel:
        """Создать новую посылку"""
        parcel = Parcel(
            session_id=session_id,
            session_seq=session_seq,
            title=parcel_data.title,
            weight_kg=parcel_data.weight_kg,
            content_value_usd=parcel_data.content_value_usd,
            type_id=parcel_data.type_id,
        )
        self.db.add(parcel)
        await self.db.commit()
        return parcel
    
    async def get_last_sequence(self, session_id: str) -> int:
        """Получить последний номер последовательности для сессии"""
        result = (await self.db.execute(
            select(func.coalesce(func.max(Parcel.session_seq), 0))
            .where(Parcel.session_id == session_id)
        )).scalar_one()
        return result
    
    async def get_parcels_with_types(
        self, 
        session_id: str, 
        type_id: Optional[int] = None,
        has_cost: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[int, List[Tuple[Parcel, ParcelType]]]:
        """Получить посылки с типами с фильтрацией и пагинацией"""
        query = select(Parcel, ParcelType).join(ParcelType).where(Parcel.session_id == session_id)
        
        if type_id is not None:
            query = query.where(Parcel.type_id == type_id)
        
        if has_cost is not None:
            if has_cost:
                query = query.where(Parcel.delivery_cost_rub.is_not(None))
            else:
                query = query.where(Parcel.delivery_cost_rub.is_(None))
        
        # Получаем общее количество
        total_query = query.with_only_columns(func.count())
        total = (await self.db.execute(total_query)).scalar()
        
        # Получаем данные с пагинацией
        data_query = query.order_by(Parcel.id).limit(limit).offset(offset)
        rows = (await self.db.execute(data_query)).all()
        
        return total, rows
    
    async def get_parcel_with_type(self, session_id: str, parcel_id: int) -> Optional[Tuple[Parcel, ParcelType]]:
        """Получить конкретную посылку с типом"""
        result = (await self.db.execute(
            select(Parcel, ParcelType)
            .join(ParcelType)
            .where(Parcel.session_id == session_id, Parcel.session_seq == parcel_id)
        )).first()
        return result
    
    def format_parcel_output(self, parcel: Parcel, parcel_type: ParcelType) -> ParcelOut:
        """Форматировать посылку для вывода"""
        return ParcelOut(
            id=parcel.session_seq,
            title=parcel.title,
            weight_kg=float(parcel.weight_kg),
            type_name=parcel_type.name,
            content_value_usd=float(parcel.content_value_usd),
            delivery_cost_rub=(
                float(parcel.delivery_cost_rub) if parcel.delivery_cost_rub else "Не рассчитано"
            ),
        )
