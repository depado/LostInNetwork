# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms.validators import IPAddress
from wtforms.ext.sqlalchemy.orm import model_form

from app import db
from app.models import Device, DeviceType, DeviceTypeCategory

DeviceForm = model_form(Device, base_class=Form, db_session=db.session, field_args={
    'ip1': {
        'validators': [IPAddress(message="Invalid IP Address")]
    },
    'ip2': {
        'validators': [IPAddress(message="Invalid IP Address")]
    }
})
DeviceTypeForm = model_form(DeviceType, base_class=Form, db_session=db.session)
DeviceTypeCategoryForm = model_form(DeviceTypeCategory, base_class=Form, db_session=db.session)

