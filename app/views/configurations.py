# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for
from flask_login import login_required

from app import app
from app.models import Configuration, Device
from app.utils import flash_default_password


@app.route("/configurations", methods=['GET', 'POST'])
@login_required
def configurations():
    flash_default_password()
    devices = Device.query.filter(Device.configurations != None).all()
    return render_template("configurations.html", active_page="configurations", devices=devices)


@app.route("/configurations/inspect/<int:configuration_id>", methods=['GET', 'POST'])
@login_required
def inspect_configuration(configuration_id):
    flash_default_password()
    return "Configuration {}".format(configuration_id)


@app.route("/configurations/delete/<int:configuration_id>")
@login_required
def delete_configuration(configuration_id):
    configuration = Configuration.query.filter_by(id=configuration_id).first_or_404()
    if configuration.delete():
        flash("Successfully deleted the Device.", "info")
    else:
        flash("Something went wrong.", "error")
    return redirect(url_for('configurations'))
