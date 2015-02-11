# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import app
from app.utils import down_cve, read_cve, update_cve

@app.route('/updates', methods=['GET', 'POST'])
@login_required
def updates():
    if request.method == 'POST':
        if request.form['getcve-btn'] == 'updatecve':
            down_cve()
            data = read_cve()
            update_cve(data)
            flash("Update finished", "info")
            return redirect(url_for('updates'))

    return render_template("updates.html")
