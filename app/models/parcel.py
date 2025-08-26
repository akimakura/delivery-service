from sqlalchemy import String, Integer, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.db.database import Base
from datetime import datetime

from app.models.parcel_type import ParcelType


class Parcel(Base):
    __tablename__ = "parcels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    session_seq: Mapped[int] = mapped_column(Integer, nullable=False)  # пер-сессионный id
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(10,3), nullable=False)
    content_value_usd: Mapped[float] = mapped_column(Numeric(12,2), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("parcel_types.id"), nullable=False)
    delivery_cost_rub: Mapped[Optional[float]] = mapped_column(Numeric(12,2))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    type: Mapped["ParcelType"] = relationship()