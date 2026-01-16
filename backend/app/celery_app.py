"""
Celery Application Configuration
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "lion_bot",
    broker=settings.get_celery_broker_url(),
    backend=settings.CELERY_RESULT_BACKEND or settings.get_redis_url(),
    include=[
        "app.tasks.notifications",
        "app.tasks.order_processing",
    ]
)

# Celery Configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.tasks.notifications.*": {"queue": "notifications"},
        "app.tasks.order_processing.*": {"queue": "orders"},
    },
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Result settings
    result_expires=3600,  # 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Check for stuck orders every 5 minutes
    "check-stuck-orders": {
        "task": "app.tasks.order_processing.check_stuck_orders",
        "schedule": 300.0,  # 5 minutes
    },
    # Send daily reports at midnight
    "send-daily-reports": {
        "task": "app.tasks.notifications.send_daily_reports",
        "schedule": 86400.0,  # 24 hours
    },
}
