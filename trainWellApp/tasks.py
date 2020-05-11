from datetime import datetime

from celery.schedules import crontab
from celery.task import task

from trainWellApp.models import Event, Place


@task
def some_task():
    print("HELLO WORLD")
