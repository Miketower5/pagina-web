from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class GastoCreate(BaseModel):
    monto: Decimal
    descripcion: str
    categoria: str
    subcategoria: str | None = None
    fuente: str
    referencia_externa: str | None = None
    fecha: datetime


class GastoRead(BaseModel):
    id: int
    monto: Decimal
    descripcion: str
    categoria: str
    subcategoria: str | None
    fuente: str
    referencia_externa: str | None
    fecha: datetime
    creado_en: datetime

    model_config = {"from_attributes": True}
