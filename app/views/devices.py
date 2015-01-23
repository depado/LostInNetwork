# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import app
from app.forms import DeviceForm, DeviceTypeForm, DeviceTypeCategoryForm, LanForm, ManufacturerForm
from app.models import Device, DeviceType, DeviceTypeCategory, Lan, Manufacturer


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
    form_dict = dict(lan_form=lan_form, device_form=device_form, devicetype_form=devicetype_form,
                     devicetypecategory_form=devicetypecategory_form,
                     manufacturer_form=manufacturer_form)

    if request.method == 'POST':
        device_form.chain_push_new(request=request, model=Device)
        devicetype_form.chain_push_new(request=request, model=DeviceType)
        devicetypecategory_form.chain_push_new(request=request, model=DeviceTypeCategory)

        lan_form.chain_push_new(request=request, model=Lan)
        manufacturer_form.chain_push_new(request=request, model=Manufacturer)

    return render_template('devices.html', devices=Device.query.all(), active_page="devices", **form_dict)


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


@app.route("/devices/inspect/<int:device_id>", methods=['GET', 'POST'])
@login_required
def inspect_device(device_id):
    """
    Inspect and edit a device and all its related object.
    """
    device = Device.query.filter_by(id=device_id).first_or_404()
    devicetype = device.devicetype

    device_form = DeviceForm(prefix="device", obj=device)
    devicetype_form = DeviceTypeForm(prefix="devicetype", obj=devicetype)
    devicetypecategory_form = DeviceTypeCategoryForm(prefix="devicetypecategory", obj=devicetype.devicetypecategory)
    lan_form = LanForm(prefix="lan", obj=device.lan)
    manufacturer_form = ManufacturerForm(prefix="manufacturer", obj=devicetype.manufacturer)

    new_lan_form = LanForm(prefix="new-lan")
    new_devicetype_form = DeviceTypeForm(prefix="new-devicetype")
    new_devicetypecategory_form = DeviceTypeCategoryForm(prefix="new-devicetypecategory")
    new_manufacturer_form = ManufacturerForm(prefix="new-manufacturer")

    if request.method == 'POST':
        device_form.chain_push_modified(request=request, model=Device, obj=device)
        devicetype_form.chain_push_modified(request=request, model=DeviceType, obj=devicetype)
        devicetypecategory_form.chain_push_modified(request=request, model=DeviceTypeCategory,
                                                    obj=devicetype.devicetypecategory)
        manufacturer_form.chain_push_modified(request=request, model=Manufacturer, obj=devicetype.manufacturer)
        lan_form.chain_push_modified(request=request, model=Lan, obj=device.lan)

        new_devicetype_form.chain_push_new(request=request, model=DeviceType)
        new_devicetypecategory_form.chain_push_new(request=request, model=DeviceTypeCategory)
        new_lan_form.chain_push_new(request=request, model=Lan)
        new_manufacturer_form.chain_push_new(request=request, model=Manufacturer)

    form_dict = dict(lan_form=lan_form, device_form=device_form, devicetype_form=devicetype_form,
                     devicetypecategory_form=devicetypecategory_form,
                     manufacturer_form=manufacturer_form, new_lan_form=new_lan_form,
                     new_devicetype_form=new_devicetype_form,
                     new_manufacturer_form=new_manufacturer_form,
                     new_devicetypecategory_form=new_devicetypecategory_form)

    return render_template("inspect_device.html", device=device, active_page="devices",
                           clear_pwd=device.decrypt_password(),**form_dict)
