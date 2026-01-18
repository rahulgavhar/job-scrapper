import os
import logging
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from app.core.config import settings

# Celery application configured via environment or defaults
celery_app = Celery(
    "job_scrapper",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=os.getenv("TZ", "UTC"),
    enable_utc=True,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)

# Autodiscover tasks in services package
celery_app.autodiscover_tasks(["app.services"])


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    """Configure Celery logger to show INFO level messages."""
    formatter = logging.Formatter(
        "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
    )
    # Ensure console handler exists and is configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    """Configure Celery task logger to show INFO level messages."""
    formatter = logging.Formatter(
        "[%(asctime)s: %(levelname)s/%(processName)s] [%(name)s] %(message)s"
    )
    # Ensure console handler exists and is configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
