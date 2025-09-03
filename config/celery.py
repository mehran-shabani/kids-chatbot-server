import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Run nightly at 00:00 Tehran (with CELERY_TIMEZONE=Asia/Tehran)
    "summarize-nightly": {
        "task": "analytics.tasks.summarize_active_threads",
        "schedule": crontab(minute=0, hour=0),
    },
    # Also run at 20:30 UTC equivalently if timezone is UTC in some envs
    "summarize-utc-2030": {
        "task": "analytics.tasks.summarize_active_threads",
        "schedule": crontab(minute=30, hour=20),
    },
}

