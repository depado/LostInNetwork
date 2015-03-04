# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.utils import down_cve, read_cve, update_cve

from app import app


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        if request.form['getcve-btn'] == 'updatecve':
            down_cve()
            data = read_cve()
            update_cve(data)
            flash("Update finished", "info")
            return redirect(url_for('updates'))

    return render_template("tasks.html", active_page="tasks")
