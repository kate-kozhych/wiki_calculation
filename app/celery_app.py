from celery import Celery

celery_app = Celery(
    "pi_calculator"
    broker="redis://localhost:6379/0" #tasks stored
    backend="redis://localhost:6379/0" #results stored
)
celery_app.conf.update(
    tesk_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_ignore_result=False,
)
celery_app.autodiscover_tasks(['app'])