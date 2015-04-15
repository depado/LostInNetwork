# -*- coding: utf-8 -*-

from celery.schedules import crontab

# Define the scheduler for Celery Beat.
# update_cve : Updates the CVE Table every day at midnight.
# scan : Scan the network every...

CELERYBEAT_SCHEDULE = {
    'update_cve': {
        'task': 'app.tasks.cve.cve_async',
        'schedule': crontab(minute=0, hour=0),
    },
    'scan': {
        'task': 'app.tasks.scan.scan_async',
        'schedule': crontab(minute=0, hour='*/3'),
    }
}
