# -*- coding: utf-8 -*-
import os
import urllib.request
from flask import session, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import app
from app.utils import downCve, readCve, startLog, updateCve

import logging

@app.route('/updates', methods=['GET', 'POST'])
@login_required
def updates():
#    if request.method == 'GET':
    if request.method == 'POST':
        if request.form['getcve-btn'] == 'updatecve':
            startLog()
            flash("Download CVE", "info")
            downCve()
            data = readCve()
            flash("Add CVE in db", "info")
            updateCve(data)
            flash("Update finished", "info")
            return redirect(url_for('updates'))

    return render_template("updates.html")
