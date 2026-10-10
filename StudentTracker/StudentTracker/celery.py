# config/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StudentTracker.settings")

app = Celery("studenttracker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()