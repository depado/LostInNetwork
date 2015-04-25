# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired


class RegisterForm(Form):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')
