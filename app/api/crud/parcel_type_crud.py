from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parcel_type import ParcelType
from app.schemas import ParcelTypeOut
from typing import List, Optional


class ParcelTypeCRUD:
    """CRUD операции для типов посылок"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_types(self) -> List[ParcelTypeOut]:
        """Получить все типы посылок"""
        rows = (await self.db.execute(select(ParcelType))).scalars().all()
        return [ParcelTypeOut(id=t.id, name=t.name) for t in rows]
    
    async def get_type_by_id(self, type_id: int) -> Optional[ParcelType]:
        """Получить тип посылки по ID"""
        result = (await self.db.execute(
            select(ParcelType).where(ParcelType.id == type_id)
        )).scalar_one_or_none()
        return result
