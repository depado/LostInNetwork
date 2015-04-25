# -*- coding: utf-8 -*-

from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.validators import DataRequired

from app import db
from app.models import Lan
from .base import CustomForm

LanForm = model_form(Lan, base_class=CustomForm, db_session=db.session, field_args={
    'name': {
        'validators': [DataRequired()],
        'description': {
            'placeholder': 'Name',
        }
    }
})
