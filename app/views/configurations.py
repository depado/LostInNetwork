# -*- coding: utf-8 -*-

from flask import render_template
from flask_login import login_required

from app import app
from app.utils import flash_default_password


@app.route("/configurations", methods=['GET', 'POST'])
@login_required
def configurations():
    flash_default_password()
    return render_template("configurations.html", active_page="configurations")


@app.route("/configurations/inspect/<int:configuration_id>", methods=['GET', 'POST'])
@login_required
def inspect_configuration(configuration_id):
    flash_default_password()
    return "Configuration {}".format(configuration_id)


@app.route("/configurations/delete/<int:configuration_id>")
@login_required
def delete_configuration(configuration_id):
    return "Delete {}".format(configuration_id)
