from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Gasto(Base):
    __tablename__ = "gastos"

    id: Mapped[int] = mapped_column(primary_key=True)
    # CBU/cuenta cifrada con pgp_sym_encrypt — nunca en texto plano
    cuenta_cifrada: Mapped[str] = mapped_column(Text, nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategoria: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fuente: Mapped[str] = mapped_column(String(50), nullable=False)  # mp | belvo | manual
    referencia_externa: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
