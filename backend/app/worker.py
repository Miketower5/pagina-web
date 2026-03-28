import logging

from celery import Celery

from app.config import settings

celery_app = Celery("gestor_gastos", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

logger = logging.getLogger(__name__)


@celery_app.task(name="procesar_pago_mp")
def procesar_pago_mp(payload: dict) -> None:
    """Procesa un evento de pago de Mercado Pago de forma asíncrona."""
    event_type = payload.get("type")
    logger.info("Procesando evento MP: %s", event_type)

    if event_type == "payment":
        _handle_payment(payload.get("data", {}))


def _handle_payment(data: dict) -> None:
    payment_id = data.get("id")
    logger.info("Procesando pago MP id=%s", payment_id)
    # TODO: consultar API de MP, clasificar y persistir el gasto
