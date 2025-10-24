"""
Celery Application Configuration
Handles background tasks and scheduled jobs.
"""

import os
from celery import Celery
from celery.schedules import crontab


def make_celery(app_name=__name__):
    """Create and configure Celery app."""
    # Use Redis as broker and backend
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    celery = Celery(
        app_name,
        broker=redis_url,
        backend=redis_url,
        include=['src.tasks']
    )
    
    # Configure Celery
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
    )
    
    # Configure periodic tasks (Beat schedule)
    celery.conf.beat_schedule = {
        'annual-step-increment': {
            'task': 'src.tasks.process_annual_step_increment',
            'schedule': crontab(hour=0, minute=0, day_of_month=1, month_of_year=1),  # January 1st at midnight
            'args': ()
        },
        'send-pending-notifications': {
            'task': 'src.tasks.send_pending_notifications',
            'schedule': crontab(minute='*/15'),  # Every 15 minutes
            'args': ()
        },
    }
    
    return celery


# Create Celery instance
celery_app = make_celery()

