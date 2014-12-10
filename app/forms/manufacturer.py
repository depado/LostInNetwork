# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

from app import db
from app.models import Manufacturer

ManufacturerForm = model_form(Manufacturer, base_class=Form, db_session=db.session)
