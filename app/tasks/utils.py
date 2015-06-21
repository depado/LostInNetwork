# -*- coding: utf-8 -*-

from app import celery

def purge_all_tasks():
    celery.control.purge()
