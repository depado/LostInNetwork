# -*- coding: utf-8 -*-

from flask import request, flash, url_for, redirect, render_template
from flask_login import login_required, current_user

from app.forms import SettingsForm
from app.models import Device
from app.utils.crypto import PasswordManager

from app import app
from app.utils import flash_default_password


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    Settings page. Allows the user to change his password.
    Re-encrypts files and device passwords using the new one. (Can take some time in case there are many devices)
    """
    flash_default_password()
    form = SettingsForm(request.form)
    if form.validate_on_submit():
        if form.newpassword.data and form.oldpassword.data and form.repeat.data:
            # Handling the decryption and re-encryption of the passwords in case of a password change
            new_pwdh = PasswordManager.generate_pwdh_from_password(form.newpassword.data)
            for device in Device.query.all():
                # Decrypts the password using the session pwdh and encrypts it with the new pwdh (not in session)
                device.password = PasswordManager.encrypt_string(device.decrypt_password(), new_pwdh)
                device.enapassword = PasswordManager.encrypt_string(device.decrypt_enapassword(), new_pwdh)
                device.save(encrypt=False)  # The password is already encrypted
            PasswordManager.set_session_pwdh(form.newpassword.data)
            current_user.set_password(form.newpassword.data)
            current_user.save()
            flash("Successfully set new password", "info")
        return redirect(url_for('settings'))
    else:
        return render_template("settings.html", form=form, active_page="settings")
