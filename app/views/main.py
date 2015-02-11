# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required

from app import app
from app.forms import LoginForm, SettingsForm
from app.models import User, Device
from app.utils.crypto import PasswordManager


@app.route('/', methods=['GET'])
@login_required
def index():
    if current_user.check_password("root"):
        flash("You still use the default password. Please change it.", "info")
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        PasswordManager.set_session_pwdh(form.password.data)
        return redirect(url_for('index'))
    else:
        return render_template("login.html", form=form)


@app.route("/test", methods=['GET'])
def test():
    print(PasswordManager.decrypt_string_from_session_pwdh(Device.query.all()[0].password))
    return "OK"


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    PasswordManager.pop_session_pwdh()
    return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(request.form)
    if form.validate_on_submit():
        if form.newpassword.data and form.oldpassword.data and form.repeat.data:
            # Handling the decryption and re-encryption of the passwords in case of a password change
            new_pwdh = PasswordManager.generate_pwdh_from_password(form.newpassword.data)
            for device in Device.query.all():
                # Decrypts the password using the session pwdh and encrypts it with the new pwdh (not in session)
                device.password = PasswordManager.encrypt_string(device.decrypt_password(), new_pwdh)
                device.save(encrypt=False)  # The password is already encrypted
            PasswordManager.set_session_pwdh(form.newpassword.data)
            current_user.set_password(form.newpassword.data)
            current_user.save()
            flash("Successfully set new password", "info")
        return redirect(url_for('settings'))
    else:
        return render_template("settings.html", form=form, active_page="settings")
