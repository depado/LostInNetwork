# -*- coding: utf-8 -*-

from flask import render_template
from flask_login import login_required

from app import app
from app.utils import flash_default_password

@app.route("/analysis", methods=['GET', 'POST'])
@login_required
def analysis():
    flash_default_password()
    return render_template("analysis.html", active_page="analysis")
