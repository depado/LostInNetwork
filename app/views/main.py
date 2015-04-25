# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required

from app.forms import LoginForm
from app.models import User
from app.utils.crypto import PasswordManager

from app import app


@app.route('/', methods=['GET'])
@login_required
def index():
    if current_user.check_password("root"):
        flash("You still use the default password. Please change it.", "info")
    return render_template("index.html")


@app.route('/sysinfo', methods=['GET'])
@login_required
def sysinfo():
    app.sysinfo.update()
    return render_template("sysinfo.html", sysinfo=app.sysinfo, active_page="sysinfo")


@app.route('/help', methods=['GET'])
def help():
    return render_template("help.html", active_page="help")


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


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    PasswordManager.pop_session_pwdh()
    return redirect(url_for('login'))
