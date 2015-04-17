# -*- coding: utf-8 -*-

from celery.schedules import crontab

# Define the scheduler for Celery Beat.
# update_cve : Updates the CVE Table every day at midnight.
# scan : Can't be run on its own. Need the password hash and therefore the user needs to be connected.
# Maybe celery can check if 

CELERYBEAT_SCHEDULE = {
    'update_cve': {
        'task': 'app.tasks.cve.cve_async',
        'schedule': crontab(minute=0, hour=0),
    },
}
