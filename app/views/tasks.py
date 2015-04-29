# -*- coding: utf-8 -*-

from flask import render_template
from flask_login import login_required

from app import app
from app.utils import flash_default_password
from app.models import Configuration


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    """
    Quite nothing to do here. Renders the template. Everything happens in async calls.
    Also detects the last scan date.
    """
    flash_default_password()
    last_conf = Configuration.query.order_by(Configuration.date.desc()).first()
    last_fetch = last_conf.date if last_conf else None
    return render_template("tasks.html", active_page="tasks", last_fetch=last_fetch)
