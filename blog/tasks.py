from celery import shared_task
import time

@shared_task
def task():
    print("Celery: task started...")
    time.sleep(5)  
    print("Celery: task finished!")
    return "task completed"
