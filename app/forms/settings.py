# -*- coding: utf-8 -*-

from flask_wtf import Form

from flask_login import current_user

from wtforms import PasswordField
from wtforms.validators import ValidationError


class SettingsForm(Form):
    oldpassword = PasswordField('old password')
    newpassword = PasswordField('new password')
    repeat = PasswordField('repeat password')

    def validate_oldpassword(self, field):
        if self.oldpassword.data:
            if not current_user.check_password(self.oldpassword.data):
                raise ValidationError("Password does not match")

    def validate_repeat(self, field):
        if self.newpassword.data and not self.repeat.data:
            raise ValidationError("Please type again your new password")
        if not self.newpassword.data == self.repeat.data:
            raise ValidationError("Passwords are different")

    def validate_newpassword(self, field):
        if self.repeat.data and not self.newpassword.data:
            raise ValidationError("Please fill in your new password")
