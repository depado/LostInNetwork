# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import app
from app.forms import DeviceForm, DeviceTypeForm, DeviceTypeCategoryForm, LanForm, ManufacturerForm
from app.models import Device, DeviceType, DeviceTypeCategory, Lan, Manufacturer


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
    """
    The devices view. Displays a list of available devices, as well as the forms to add a new one.
    As this view contains many forms, there is a mechanism to display them all and get only the one submitted.
    Example :
    In template :
        <button type="submit" class="btn btn-primary" name="btn" value="{{ device_form._prefix }}save-btn">
            <span>Save</span>
        </button>
    The value will be : 
        device-save-btn
    """
    lan_form = LanForm(prefix="lan")
    device_form = DeviceForm(prefix="device")
    devicetype_form = DeviceTypeForm(prefix="devicetype")
    devicetypecategory_form = DeviceTypeCategoryForm(prefix="devicetypecategory")
    manufacturer_form = ManufacturerForm(prefix="manufacturer")

    if request.method == 'POST':
        device_form.chain_push_new(request=request, model=Device)
        devicetype_form.chain_push_new(request=request, model=DeviceType)
        devicetypecategory_form.chain_push_new(request=request, model=DeviceTypeCategory)

        lan_form.chain_push_new(request=request, model=Lan)
        manufacturer_form.chain_push_new(request=request, model=Manufacturer)

    return render_template('devices.html', devices=Device.query.all(), device_form=device_form,
                           devicetype_form=devicetype_form, devicetypecategory_form=devicetypecategory_form,
                           lan_form=lan_form, manufacturer_form=manufacturer_form, active_page="devices")


@app.route("/devices/delete/<int:device_id>", methods=['GET'])
@login_required
def delete_device(device_id):
    """
    View to delete a device. This doesn't render a template.
    This behaviour may be changed to display a template with an option to cascade delete all the
    related items (foreign keys and stuff like that).

    :param device_id: The ID of the device to be deleted.
    """
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


@app.route("/devices/inspect/<int:device_id>", methods=['GET', 'POST'])
@login_required
def inspect_device(device_id):
    device = Device.query.filter_by(id=device_id).first_or_404()
    return render_template("inspect_device.html", device=device, active_page="devices")
