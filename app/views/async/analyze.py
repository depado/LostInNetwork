# -*- coding: utf-8 -*-

import time

from flask import jsonify, url_for, redirect

from app import app, celery

@celery.task(bind=True)
def test_bg_task(self):
    """
    Test task that updates the status of the task every 100ms
    """
    for i in range(0, 100):
        self.update_state(state='PROGRESS', meta={'percentage': i})
        time.sleep(0.1)


@app.route("/test_long_task")
def long_task():
    task = test_bg_task.apply_async()
    return redirect(url_for('task_status', task_id=task.id))


@app.route("/status/<task_id>")
def task_status(task_id):
    task = test_bg_task.AsyncResult(task_id)
    return jsonify({
        'state': task.state,
        'percentage': task.info.get('percentage', 0),
    })
