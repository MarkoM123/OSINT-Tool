from celery import Celery

from core.config import get_settings

settings = get_settings()

celery_app = Celery("eip_tasks", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_routes=settings.celery_task_routes)
