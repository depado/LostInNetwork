# -*- coding: utf-8 -*-

from celery.schedules import crontab


BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

CELERYBEAT_SCHEDULE = {
    'update_cve': {
        'task': 'app.tasks.cve.cve_async',
        'schedule': crontab(minute=0, hour=0),
    },
}
