from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.gasto import Gasto
from app.schemas.gasto import GastoCreate, GastoRead

router = APIRouter()


@router.get("/", response_model=list[GastoRead])
async def listar_gastos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Gasto).order_by(Gasto.fecha.desc()))
    return result.scalars().all()


@router.get("/{gasto_id}", response_model=GastoRead)
async def obtener_gasto(gasto_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Gasto).where(Gasto.id == gasto_id))
    gasto = result.scalar_one_or_none()
    if gasto is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return gasto
