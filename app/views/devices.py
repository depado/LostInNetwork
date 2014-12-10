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


def push_new_from_form(model, form):
    """
    Automatically create the object and save it from the data in the form.
    Automatic rollback of the database in case of error.

    :param model: The model associated to the form.
    :param form: The form with data inside.
    """
    instance = model()
    form.populate_obj(instance)
    if instance.save():
        flash("{} created and saved.".format(getattr(instance, "friendly_name", instance.__class__.__name__)), "info")
    else:
        flash("Something went wrong.", "error")


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
                push_new_from_form(Device, device_form)

        elif has_clicked(request, devicetype_form):
            if devicetype_form.validate_on_submit():
                push_new_from_form(DeviceType, devicetype_form)

        elif has_clicked(request, devicetypecategory_form):
            if devicetypecategory_form.validate_on_submit():
                push_new_from_form(DeviceTypeCategory, devicetypecategory_form)

        elif has_clicked(request, lan_form):
            if lan_form.validate_on_submit():
                push_new_from_form(Lan, lan_form)

        elif has_clicked(request, manufacturer_form):
            if manufacturer_form.validate_on_submit():
                push_new_from_form(Manufacturer, manufacturer_form)

    return render_template('devices.html', devices=Device.query.all(), device_form=device_form,
                           devicetype_form=devicetype_form, devicetypecategory_form=devicetypecategory_form,
                           lan_form=lan_form, manufacturer_form=manufacturer_form, active_page="devices")


@app.route("/devices/delete/<int:device_id>", methods=['GET'])
@login_required
def delete_device(device_id):
    device = Device.query.filter_by(id=device_id).first_or_404()
    if device.delete():
        flash("Successfully deleted the Device.", "info")
    else:
        flash("Something went wrong.", "error")
    return redirect(url_for('devices'))


@app.route("/devices/edit/<int:device_id>", methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    device = Device.query.filter_by(id=device_id).first_or_404()
    form = DeviceForm(obj=device)
    if form.validate_on_submit():
        form.populate_obj(device)
        if device.save():
            flash("Device successfully edited.", "info")
        else:
            flash("Something went wrong.", "error")
        return redirect(url_for('devices'))
    return render_template("edit_device.html", form=form, active_page="devices")
