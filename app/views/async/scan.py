# -*- coding: utf-8 -*-

import redis

from flask import jsonify
from flask_login import login_required

from app import app
from app.tasks import scan_all_devices_async
from app.tasks.scan import SCAN_KEY
from app.utils.crypto import PasswordManager


@app.route('/start/scan', methods=['POST'])
@login_required
def start_scan_all_devices_async():
    """
    Starts the scan and set the lock.
    """
    task = scan_all_devices_async.apply_async((PasswordManager.get_session_pwdh(),))
    redis.Redis().set(SCAN_KEY, task.id)
    return jsonify({'key': task.id})
