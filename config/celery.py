import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "summarize-midnight": {
        "task": "analytics.tasks.summarize_active_threads",
        "schedule": crontab(minute=0, hour=0),
    },
    "summarize-0030": {
        "task": "analytics.tasks.summarize_active_threads",
        "schedule": crontab(minute=30, hour=0),
    },
}

