# -*- coding: utf-8 -*-

import redis

from flask import jsonify
from flask_login import login_required

from app import app
from app.tasks.cve import cve_async, CVE_LOCK, CVE_KEY
from .lock import lock_available


@app.route('/start/cve_update', methods=['POST'])
@login_required
def async_cve_update():
    """
    Starts the CVE update and set the lock.
    """
    task = cve_async.apply_async()
    redis.Redis().set(CVE_KEY, task.id)
    return jsonify({'key': task.id})


@app.route('/status/cve_update', methods=['GET'])
@login_required
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
