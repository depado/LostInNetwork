# -*- coding: utf-8 -*-

from flask_login import login_required

from app import app


@app.route("/configurations", methods=['GET', 'POST'])
@login_required
def configurations():
    return "Configurations"


@app.route("/configurations/inspect/<int:configuration_id>", methods=['GET', 'POST'])
@login_required
def inspect_configuration(configuration_id):
    return "Configuration {}".format(configuration_id)


@app.route("/configurations/delete/<int:configuration_id>")
@login_required
def delete_configuration(configuration_id):
    return "Delete {}".format(configuration_id)
