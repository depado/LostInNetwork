# -*- coding: utf-8 -*-

import os

from flask import render_template, flash, redirect, url_for, make_response
from flask_login import login_required

from app import app
from app.models import Configuration, Device
from app.utils import flash_default_password
from app.utils.crypto import PasswordManager


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
    configuration = Configuration.query.filter_by(id=configuration_id).first_or_404()
    try:
        content = PasswordManager.decrypt_file_content_from_session_pwdh(configuration.path)
        return render_template("inspect_configuration.html", content=content, active_page='configurations')
    except Exception as e:
        app.logger.exception(msg="Something went wrong : {}".format(e))
        return redirect(url_for('configurations'))


@app.route("/configurations/delete/<int:configuration_id>")
@login_required
def delete_configuration(configuration_id):
    configuration = Configuration.query.filter_by(id=configuration_id).first_or_404()
    if configuration.delete():
        flash("Successfully deleted the configuration.", "info")
    else:
        flash("Something went wrong.", "error")
    return redirect(url_for('configurations'))


@app.route("/configurations/download/<int:configuration_id>")
@login_required
def download_configuration(configuration_id):
    configuration = Configuration.query.filter_by(id=configuration_id).first_or_404()
    try:
        content = PasswordManager.decrypt_file_content_from_session_pwdh(configuration.path)
        directory, filename = os.path.split(configuration.path)
        response = make_response(content)
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
        return response
    except Exception as e:
        app.logger.exception(msg="Something went wrong while downloading configuration : {}".format(e))
        flash("Something went wrong. Check the log file for more information.", "error")
        return redirect(url_for('configurations'))
