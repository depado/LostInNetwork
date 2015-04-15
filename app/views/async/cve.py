# -*- coding: utf-8 -*-

import redis

from flask import jsonify

from app import app
from app.tasks.cve import cve_async, CVE_LOCK, CVE_KEY

SCAN_KEY = "scan_task_uuid"
SCAN_LOCK = redis.Redis().lock("celery_scan_lock")


def lock_available(lock):
    free_lock = False
    try:
        free_lock = lock.acquire(blocking=False)
    finally:
        if free_lock:
            lock.release()
            return True
        else:
            return False


@app.route('/async_cve_update', methods=['POST'])
def async_cve_update():
    """
    Starts the CVE update and set the lock.
    """
    task = cve_async.apply_async()
    redis.Redis().set(CVE_KEY, task.id)
    return jsonify({'key': task.id})

@app.route('/async_update_cve/status', methods=['GET'])
def async_cve_update_status():
    """
    Ajax call to get the CVE Update status
    """
    if not lock_available(CVE_LOCK):
        task = cve_async.AsyncResult(redis.Redis().get(CVE_KEY))
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
