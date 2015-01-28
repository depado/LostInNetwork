# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import app

@app.route('/updates', methods=['GET'])
@login_required
def updates():
    return render_template("updates.html")
