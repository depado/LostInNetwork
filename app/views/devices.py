# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import app
from app.forms import DeviceForm, DeviceTypeForm, DeviceTypeCategoryForm, LanForm, ManufacturerForm
from app.models import Device, DeviceType, DeviceTypeCategory, Lan, Manufacturer


def has_clicked(req, form):
    """
    Returns whether it was this form or not that was submitted.

    :param req: The flask request of the route
    :param form: The form that may have been submitted or not
    :return: True if form has been submitted, False otherwise
    """
    return req.form['btn'] == "{prefix}save-btn".format(prefix=form._prefix)

@app.route('/devices', methods=['GET', 'POST'])
@login_required
def devices():
    lan_form = LanForm(prefix="lan")
    device_form = DeviceForm(prefix="device")
    devicetype_form = DeviceTypeForm(prefix="devicetype")
    devicetypecategory_form = DeviceTypeCategoryForm(prefix="devicetypecategory")
    manufacturer_form = ManufacturerForm(prefix="manufacturer")

    if request.method == 'POST':
        if has_clicked(request, device_form):
            if device_form.validate_on_submit():
                device = Device(name=device_form.name.data, ip1=device_form.ip1.data, ip2=device_form.ip2.data,
                                devicetype=device_form.devicetype.data, lan=device_form.lan.data)
                if device.save():
                    flash("Successfully created the Device.")
                else:
                    flash("Something went wrong.")

        elif has_clicked(request, devicetype_form):
            if devicetype_form.validate_on_submit():
                devicetype = DeviceType(name=devicetype_form.name.data, manufacturer=devicetype_form.manufacturer.data,
                                        devicetypecategory=devicetype_form.devicetypecategory.data)
                if devicetype.save():
                    flash("Successfully created the Device Type.")
                else:
                    flash("Something went wrong.")

        elif has_clicked(request, devicetypecategory_form):
            if devicetypecategory_form.validate_on_submit():
                devicetypecategory = DeviceTypeCategory(name=devicetypecategory_form.name.data)
                if devicetypecategory.save():
                    flash("Successfully created the Device Type Category.")
                else:
                    flash("Something went wrong.")

        elif has_clicked(request, lan_form):
            if lan_form.validate_on_submit():
                lan = Lan(name=lan_form.name.data)
                if lan.save():
                    flash("Successfully created the Lan.")
                else:
                    flash("Something went wrong.")

        elif has_clicked(request, manufacturer_form):
            if manufacturer_form.validate_on_submit():
                manufacturer = Manufacturer(name=manufacturer_form.name.data)
                if manufacturer.save():
                    flash("Successfully created the Manufacturer.")
                else:
                    flash("Something went wrong.")

    return render_template('devices.html', devices=Device.query.all(), device_form=device_form,
                           devicetype_form=devicetype_form, devicetypecategory_form=devicetypecategory_form,
                           lan_form=lan_form, manufacturer_form=manufacturer_form, active_page="devices")

@app.route("/devices/delete/<int:device_id>")
def delete_device(device_id):
    device = Device.query.filter_by(id=device_id).first_or_404()
    device.delete()
    flash("Successfully deleted the Device.")
    return redirect(url_for('devices'))

