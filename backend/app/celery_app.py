"""
Celery Application Configuration

Celery app instance with Redis broker for background tasks and scheduled jobs.
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import get_settings

settings = get_settings()

# Create Celery instance
celery_app = Celery(
    "flexiprice",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,  # Number of tasks to prefetch per worker
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (prevent memory leaks)
    worker_concurrency=8,  # Number of concurrent worker processes (adjust based on CPU cores)
    task_acks_late=True,  # Acknowledge tasks after completion (safer for failures)
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
    result_expires=3600,  # Results expire after 1 hour
    task_compression="gzip",  # Compress task messages for network efficiency
)

# Celery Beat Schedule - Periodic Tasks
celery_app.conf.beat_schedule = {
    # Recompute discounts every hour
    "recompute-all-discounts": {
        "task": "app.tasks.recompute_all_discounts",
        "schedule": crontab(minute=0),  # Every hour at minute 0
        "options": {"expires": 3600}  # Expire after 1 hour
    },
    # Cleanup expired discounts every day at 2 AM
    "cleanup-expired-discounts": {
        "task": "app.tasks.cleanup_expired_discounts",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
        "options": {"expires": 86400}  # Expire after 1 day
    },
    # Update price history every 6 hours
    "update-price-history": {
        "task": "app.tasks.update_price_history",
        "schedule": crontab(hour="*/6", minute=0),  # Every 6 hours
        "options": {"expires": 21600}  # Expire after 6 hours
    },
}

# Optional: Custom task routes
celery_app.conf.task_routes = {
    "app.tasks.recompute_all_discounts": {"queue": "discounts"},
    "app.tasks.recompute_batch_chunk": {"queue": "discounts"},  # Parallel chunk processing
    "app.tasks.parallel_recompute_discounts": {"queue": "discounts"},
    "app.tasks.cleanup_expired_discounts": {"queue": "maintenance"},
    "app.tasks.update_price_history": {"queue": "analytics"},
}

# Task priority configuration (0-9, higher = more priority)
celery_app.conf.task_default_priority = 5
celery_app.conf.broker_transport_options = {
    "priority_steps": [0, 3, 6, 9],  # Support for priority levels
    "queue_order_strategy": "priority",  # Process higher priority tasks first
}
