import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def _verificar_firma_mp(payload: bytes, signature: str) -> bool:
    """Valida la firma HMAC-SHA256 enviada por Mercado Pago."""
    expected = hmac.new(
        settings.mp_webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/mercadopago")
async def webhook_mercadopago(
    request: Request,
    x_signature: str = Header(..., alias="x-signature"),
):
    payload = await request.body()

    if not _verificar_firma_mp(payload, x_signature):
        raise HTTPException(status_code=401, detail="Firma inválida")

    data = await request.json()
    logger.info("Webhook MP recibido: type=%s", data.get("type"))

    # Encolar procesamiento asíncrono
    from app.worker import procesar_pago_mp
    procesar_pago_mp.delay(data)

    return {"status": "accepted"}
