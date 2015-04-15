# -*- coding: utf-8 -*-

from flask import flash
from flask_login import current_user

def flash_default_password():
    if current_user.check_password("root"):
        flash("You still use the default password. Please change it.", "info")
