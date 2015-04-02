# -*- coding: utf-8 -*-

import time
import redis

from flask import jsonify

from app import app, celery
from app.utils import down_cve, read_cve, update_cve

CVE_KEY = "cve_task_uuid"
CVE_LOCK = redis.Redis().lock("celery_cve_lock")


def lock_available():
    free_lock = False
    try:
        free_lock = CVE_LOCK.acquire(blocking=False)
    finally:
        if free_lock:
            CVE_LOCK.release()
            return True
        else:
            return False


@celery.task(bind=True)
def async_cve(self):
    have_lock = False
    try:
        have_lock = CVE_LOCK.acquire(blocking=False)
        self.update_state(state='PROGRESS', meta={'message': "Started CVE Update", 'percentage': 5})
        self.update_state(state='PROGRESS', meta={'message': "Downloading CVE", 'percentage': 5})
        down_cve()
        self.update_state(state='PROGRESS', meta={'message': "Reading CVE", 'percentage': 30})
        data = read_cve()
        self.update_state(state='PROGRESS', meta={'message': "Updating CVE", 'percentage': 65})
        update_cve(data)
        self.update_state(state='PROGRESS', meta={'message': "Done", 'percentage': 100})
        time.sleep(10)
    finally:
        if have_lock:
            CVE_LOCK.release()
        else:
            print("Didn't have lock")


@app.route('/async_cve_update', methods=['POST'])
def async_cve_update():
    task = async_cve.apply_async()
    redis.Redis().set(CVE_KEY, task.id)
    return jsonify({'key': task.id})

@app.route('/async_update_cve/status', methods=['GET'])
def async_cve_update_status():

    if not lock_available():
        task = async_cve.AsyncResult(redis.Redis().get(CVE_KEY))
        if task.state == 'PENDING':
            response = {
                'started': True,
                'state': task.state,
                'message': 'Pending...',
                'percentage': 0,
            }
        elif task.state != 'FAILURE':
            response = {
                'started': True,
                'state': task.state,
                'message': task.info.get('message', ''),
                'percentage': task.info.get('percentage', '')
            }
        else:
            response = {
                'started': True,
                'state': task.state,
                'message': task.info.get('message', ''),
                'percentage': task.info.get('percentage', ''),
                'status': str(task.info),
            }
        return jsonify(response)
    else:
        return jsonify({'started': False})
