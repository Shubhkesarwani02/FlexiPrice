# Celery Background Tasks Setup

## Overview

FlexiPrice uses Celery for background task processing and periodic scheduling:

- **Celery Worker**: Processes asynchronous tasks
- **Celery Beat**: Schedules periodic tasks (cron-like)
- **Redis**: Message broker and result backend

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   FastAPI   │────────▶│    Redis    │◀────────│Celery Worker │
│   Backend   │         │   (Broker)  │         │              │
└─────────────┘         └─────────────┘         └──────────────┘
                               ▲
                               │
                        ┌──────┴───────┐
                        │ Celery Beat  │
                        │  (Scheduler) │
                        └──────────────┘
```

## Scheduled Tasks

### 1. Discount Recomputation (Hourly)
- **Task**: `recompute_all_discounts`
- **Schedule**: Every hour at minute 0
- **Purpose**: Recalculate discounts for all batches expiring within 30 days
- **Queue**: `discounts`

### 2. Expired Discount Cleanup (Daily)
- **Task**: `cleanup_expired_discounts`
- **Schedule**: Daily at 2:00 AM
- **Purpose**: Mark old discounts as expired
- **Queue**: `maintenance`

### 3. Price History Update (Every 6 hours)
- **Task**: `update_price_history`
- **Schedule**: Every 6 hours
- **Purpose**: Record price snapshots for analytics
- **Queue**: `analytics`

## Quick Start

### Using Docker Compose

```bash
# Start all services (backend + worker + beat)
docker-compose up -d

# Check worker logs
docker logs flexiprice-celery-worker

# Check beat logs
docker logs flexiprice-celery-beat

# Restart worker
docker-compose restart celery-worker
```

### Manual Start (Development)

```bash
# Terminal 1: Start Celery Worker
cd backend
celery -A app.celery_app worker --loglevel=info --concurrency=2

# Terminal 2: Start Celery Beat
celery -A app.celery_app beat --loglevel=info

# Terminal 3 (Optional): Start Flower monitoring
celery -A app.celery_app flower --port=5555
```

### Using Management Script

```bash
cd backend

# Start worker
python scripts/celery_manager.py worker

# Start beat scheduler
python scripts/celery_manager.py beat

# Start Flower monitoring UI
python scripts/celery_manager.py flower

# Check active tasks
python scripts/celery_manager.py active

# Check scheduled tasks
python scripts/celery_manager.py scheduled

# Purge all pending tasks
python scripts/celery_manager.py purge
```

## API Endpoints

### Manual Trigger

```bash
# Trigger discount recomputation (async)
curl -X POST "http://localhost:8000/api/v1/admin/discounts/trigger-recompute?days_threshold=30&async_task=true"

# Trigger discount recomputation (synchronous)
curl -X POST "http://localhost:8000/api/v1/admin/discounts/trigger-recompute?async_task=false"
```

### Check Task Status

```bash
# Get task status by ID
curl "http://localhost:8000/api/v1/admin/discounts/task-status/{task_id}"
```

## Configuration

### Celery Settings (`app/celery_app.py`)

```python
# Broker and Backend
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

# Task Settings
task_time_limit = 30 * 60  # 30 minutes
task_soft_time_limit = 25 * 60  # 25 minutes
worker_prefetch_multiplier = 4
worker_max_tasks_per_child = 1000
```

### Custom Schedule

Edit `app/celery_app.py` to modify the schedule:

```python
celery_app.conf.beat_schedule = {
    "recompute-all-discounts": {
        "task": "app.tasks.recompute_all_discounts",
        "schedule": crontab(minute=0),  # Every hour
    },
}
```

**Crontab Examples:**
- `crontab(minute=0)` - Every hour at minute 0
- `crontab(minute=0, hour=0)` - Daily at midnight
- `crontab(minute=0, hour="*/6")` - Every 6 hours
- `crontab(minute=0, hour=0, day_of_week=1)` - Every Monday at midnight
- `crontab(minute="*/15")` - Every 15 minutes

## Monitoring

### Flower Web UI

Access at: `http://localhost:5555`

Features:
- Real-time task monitoring
- Task history
- Worker status
- Task statistics
- Task retry/revoke

### CLI Inspection

```bash
# Active tasks
celery -A app.celery_app inspect active

# Scheduled tasks
celery -A app.celery_app inspect scheduled

# Registered tasks
celery -A app.celery_app inspect registered

# Worker stats
celery -A app.celery_app inspect stats
```

## Task Development

### Creating a New Task

```python
# In app/tasks.py
from app.celery_app import celery_app

@celery_app.task(name="app.tasks.my_custom_task")
def my_custom_task(param1: str, param2: int):
    """Your task description."""
    # Task logic here
    return {"status": "success"}
```

### Calling Tasks

```python
# Asynchronous (recommended)
from app.tasks import my_custom_task
result = my_custom_task.delay("value", 42)

# With callback
result = my_custom_task.apply_async(
    args=["value", 42],
    countdown=60,  # Execute after 60 seconds
    expires=3600,  # Expire after 1 hour
)

# Check result
if result.ready():
    print(result.result)
```

## Troubleshooting

### Worker Not Starting

```bash
# Check Redis connection
redis-cli ping

# Check Celery can import app
python -c "from app.celery_app import celery_app; print(celery_app)"

# Start worker with debug logging
celery -A app.celery_app worker --loglevel=debug
```

### Tasks Not Executing

```bash
# Check if tasks are registered
celery -A app.celery_app inspect registered

# Check active tasks
celery -A app.celery_app inspect active

# Purge old tasks
celery -A app.celery_app purge
```

### Beat Not Scheduling

```bash
# Remove old beat schedule file
rm celerybeat-schedule

# Restart beat with debug logging
celery -A app.celery_app beat --loglevel=debug
```

## Production Deployment

### Systemd Service Files

**Worker Service** (`/etc/systemd/system/flexiprice-celery.service`):

```ini
[Unit]
Description=FlexiPrice Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=flexiprice
Group=flexiprice
WorkingDirectory=/opt/flexiprice/backend
Environment="PATH=/opt/flexiprice/venv/bin"
ExecStart=/opt/flexiprice/venv/bin/celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --pidfile=/var/run/celery/worker.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

**Beat Service** (`/etc/systemd/system/flexiprice-beat.service`):

```ini
[Unit]
Description=FlexiPrice Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=flexiprice
Group=flexiprice
WorkingDirectory=/opt/flexiprice/backend
Environment="PATH=/opt/flexiprice/venv/bin"
ExecStart=/opt/flexiprice/venv/bin/celery -A app.celery_app beat \
    --loglevel=info \
    --pidfile=/var/run/celery/beat.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

### Enable and Start

```bash
sudo systemctl enable flexiprice-celery flexiprice-beat
sudo systemctl start flexiprice-celery flexiprice-beat
sudo systemctl status flexiprice-celery flexiprice-beat
```

## Best Practices

1. **Idempotent Tasks**: Design tasks to be safely retried
2. **Time Limits**: Set appropriate time limits for all tasks
3. **Error Handling**: Use try/except and log errors properly
4. **Task Routing**: Use different queues for different task types
5. **Monitoring**: Always monitor task execution and worker health
6. **Graceful Shutdown**: Allow tasks to finish before stopping workers

## References

- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Monitoring](https://flower.readthedocs.io/)
