# -*- coding: utf-8 -*-
import os
import pickle
from flask import session, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import app
from app.utils import downCve, updateCve, upCve

@app.route('/updates', methods=['GET', 'POST'])
@login_required
def updates():
#    if request.method == 'GET':
    if request.method == 'POST':
        if request.form['getcve-btn'] == 'updatecve':
            flash("Download and update CVE", "info")
#            downCve()
#            updateCve()
            upCve()
            return redirect(url_for('updates'))

    return render_template("updates.html")
