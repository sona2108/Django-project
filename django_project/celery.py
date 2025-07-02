from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

app = Celery(
    'django_project',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.timezone = 'Asia/Kolkata'
app.conf.enable_utc = False

# In your Celery config
broker_connection_retry_on_startup = True
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'