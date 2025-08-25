from app.db.database import Base
from .parcel import Parcel
from .parcel_type import ParcelType

__all__ = ["Base", "Parcel", "ParcelType"]
