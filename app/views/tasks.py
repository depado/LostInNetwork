# -*- coding: utf-8 -*-

from flask import render_template
from flask_login import login_required

from app import app


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    return render_template("tasks.html", active_page="tasks")
