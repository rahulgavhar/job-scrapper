#!/usr/bin/env python3
"""
Start script for Render deployment
Runs Celery worker and FastAPI in a single process with unified logging
"""
import os
import sys
import logging
import multiprocessing

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def start_celery_worker():
    """Start Celery worker in background process"""
    from app.celery_app import celery_app

    logger.info("Starting Celery worker...")

    # Create worker instance
    worker = celery_app.Worker(
        pool='solo',  # Use solo pool for compatibility
        loglevel='INFO',
        logfile=None,  # Log to stdout
    )

    worker.start()


def start_api_server():
    """Start FastAPI server"""
    import uvicorn

    logger.info("Starting FastAPI server...")

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "10000"))

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Job Scraper Application")
    logger.info("=" * 60)

    # Check Redis connection
    broker_url = os.getenv("CELERY_BROKER_URL")
    if broker_url:
        logger.info(f"Celery Broker: {broker_url[:30]}...")
    else:
        logger.warning("CELERY_BROKER_URL not set - using default")

    # Start Celery worker in background process
    worker_process = multiprocessing.Process(target=start_celery_worker, daemon=True)
    worker_process.start()
    logger.info(f"Celery worker started (PID: {worker_process.pid})")

    # Start API server in main process (blocks)
    try:
        start_api_server()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        worker_process.terminate()
        worker_process.join()
        logger.info("Shutdown complete")

