# -*- coding: utf-8 -*-

import redis

from flask import jsonify
from flask_login import login_required

from app import app
from app.tasks.analysis import ANALYSE_KEY, ANALYSE_LOCK, async_analysis

from .lock import lock_available


@app.route('/start/analysis', methods=['POST'])
@login_required
def async_analysis_start():
    """
    Starts the Analysis and set the lock.
    """
    task = async_analysis.apply_async()
    redis.Redis().set(ANALYSE_KEY, task.id)
    return jsonify({'key': task.id})


@app.route('/status/analysis', methods=['GET'])
@login_required
def async_analysis_status():
    """
    Ajax call to get the CVE Update status
    """
    if not lock_available(ANALYSE_LOCK):
        task = async_analysis.AsyncResult(redis.Redis().get(ANALYSE_KEY))
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
