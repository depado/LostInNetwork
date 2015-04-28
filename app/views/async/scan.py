# -*- coding: utf-8 -*-

import redis

from flask import jsonify
from flask_login import login_required

from app import app
from app.tasks.scan import SCAN_KEY, SCAN_LOCK, scan_all_devices_async
from app.utils.crypto import PasswordManager

from .lock import lock_available


@app.route('/start/scan', methods=['POST'])
@login_required
def start_scan_all_devices_async():
    """
    Starts the scan and set the lock.
    """
    task = scan_all_devices_async.apply_async((PasswordManager.get_session_pwdh(),))
    redis.Redis().set(SCAN_KEY, task.id)
    return jsonify({'key': task.id})


@app.route('/status/scan', methods=['GET'])
@login_required
def scan_all_devices_async_status():
    if not lock_available(SCAN_LOCK):
        task = scan_all_devices_async.AsyncResult(redis.Redis().get(SCAN_KEY))
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
