# -*- coding: utf-8 -*-

from flask import render_template
from flask_login import login_required

from app import app
from app.forms import DeviceForm, DeviceTypeForm
from app.models import Device

@app.route('/devices', methods=['GET'])
@login_required
def devices():
    device_form = DeviceForm(prefix="device")
    devicetype_form = DeviceTypeForm(prefix="devicetype")
    return render_template('devices.html', devices=Device.query.all(),
                           device_form=device_form, devicetype_form=devicetype_form)
