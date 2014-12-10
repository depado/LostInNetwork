# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms.validators import IPAddress, DataRequired, Optional
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.widgets import PasswordInput

from app import db
from app.models import Device, DeviceType, DeviceTypeCategory

DeviceForm = model_form(Device, base_class=Form, db_session=db.session, field_args={
    'name': {
        'validators': [DataRequired()]
    },
    'ip1': {
        'validators': [DataRequired(), IPAddress(message="Invalid IP Address")]
    },
    'ip2': {
        'validators': [Optional(), IPAddress(message="Invalid IP Address")]
    },
    'password': {
        'widget': PasswordInput(),
        'validators': [DataRequired()]
    }
})
DeviceTypeForm = model_form(DeviceType, base_class=Form, db_session=db.session)
DeviceTypeCategoryForm = model_form(DeviceTypeCategory, base_class=Form, db_session=db.session)

