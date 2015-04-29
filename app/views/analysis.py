# -*- coding: utf-8 -*-

from flask import render_template, url_for
from flask_login import login_required

from app import app
from app.utils import flash_default_password
from app.models import Device
from app.views.utils import generate_analysis_dict

@app.route("/analysis", methods=['GET', 'POST'])
@login_required
def analysis():
    flash_default_password()
    data_dict = dict()
    for device in Device.query.all():
        data_dict.update(generate_analysis_dict(device))
    return render_template("analysis.html", active_page="analysis", data_dict=data_dict)
