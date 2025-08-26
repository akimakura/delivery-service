from pydantic import BaseModel, Field, condecimal
from typing import Optional, Union, List, Dict


class ParcelIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    weight_kg: condecimal(gt=0, max_digits=10, decimal_places=3)
    type_id: int
    content_value_usd: condecimal(ge=0, max_digits=12, decimal_places=2)

class ParcelOut(BaseModel):
    id: int                # session_seq
    title: str
    weight_kg: float
    type_name: str
    content_value_usd: float
    delivery_cost_rub: Optional[Union[float, str]]  # "Не рассчитано"

class ParcelTypeOut(BaseModel):
    id: int
    name: str

class Page(BaseModel):
    total: int
    items: List[ParcelOut]

class Envelope(BaseModel):
    success: bool
    data: Optional[Union[Dict, List]] = None
    error: Optional[Dict] = None
