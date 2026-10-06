import time
import logging
from celery import Celery
from app.cache.redis_cache import cache_prediction
from app.services.storage_service import delete_image
from app.cache.metrics import model_inferences
from app.config import settings

MAX_TASK_RETRIES = 3
logger = logging.getLogger(__name__)

celery_app = Celery(

    "image_classification",
    broker = settings.celery_broker_url,
    backend= settings.celery_result_backend
)
celery_app.conf.update(
    task_serializer= "json",
    result_serializer = "json",
    accept_content = ["json"],
    task_track_started = True,
    task_time_limit = 10,
    task_soft_time_limit = 8,
    result_expires = 3600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_default_queue="celery",
)

@celery_app.task(
    bind = True,
    autoretry_for =(Exception,),
    retry_backoff = True,
    retry_kwargs={"max_retries": MAX_TASK_RETRIES}
)
def classify_image(
    self,
    image_path : str,
    image_hash : str
):
    try:
        self.update_state(
            state = "PROCESSING",
            meta = {
                "message" : "Running model inference"
            }
        )
        model_inferences.inc()
        time.sleep(1.5)
        predictions = [
            {
                "class_name": "meme",
                "confidence": 0.94,
            },
            {
                "class_name": "humor",
                "confidence": 0.88,
            },
            {
                "class_name": "social_media",
                "confidence": 0.81,
            },
            {
                "class_name": "image",
                "confidence": 0.76,
            },
            {
                "class_name": "other",
                "confidence": 0.62,
            },
        ]
        result = {
            "predictions": predictions
        }
        cache_prediction(
            image_hash,
            result
        )
    except Exception:
        # Keep the input available for Celery's next retry. Celery's request
        # retry counter is 0 for the first attempt and reaches MAX_TASK_RETRIES
        # on the final attempt.
        if self.request.retries >= MAX_TASK_RETRIES:
            _delete_image_safely(image_path)
        raise
    else:
        _delete_image_safely(image_path)
        return result


def _delete_image_safely(image_path: str) -> None:
    try:
        delete_image(image_path)
    except OSError:
        # A cleanup failure should be visible in logs, but must not turn a
        # successful inference into a retry (which could duplicate work).
        logger.exception("Could not delete temporary image %s", image_path)


