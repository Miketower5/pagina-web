from fastapi import APIRouter

from app.categorizer.rules_ar import CATEGORIAS_AR

router = APIRouter()


@router.get("/")
async def listar_categorias():
    return {"categorias": list(CATEGORIAS_AR.keys())}


@router.get("/{categoria}")
async def obtener_categoria(categoria: str):
    if categoria not in CATEGORIAS_AR:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"categoria": categoria, "reglas": CATEGORIAS_AR[categoria]}
