# -*- coding: utf-8 -*-

from flask_wtf import Form

from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, ValidationError

from app import db
from app.models import User


class LoginForm(Form):
    username = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')

    def validate_username(self, field):
        user = db.session.query(User).filter_by(username=self.username.data).first()
        if user is None:
            raise ValidationError('Invalid username or password')
        if not user.check_password(self.password.data):
            raise ValidationError('Invalid username or password')
