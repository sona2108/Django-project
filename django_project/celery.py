from celery import Celery

app = Celery(
    'django_project',
    broker='redis://redis:6379/0',     
    backend='redis://redis:6379/0'     
)

app.autodiscover_tasks()
