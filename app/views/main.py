# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required

from app.forms import LoginForm
from app.models import User
from app.utils.crypto import PasswordManager
from app.utils import flash_default_password

from app import app


@app.route('/', methods=['GET'])
@login_required
def index():
    flash_default_password()
    return render_template("index.html")


@app.route('/sysinfo', methods=['GET'])
@login_required
def sysinfo():
    """
    Get the system information page. Refresh the system information on each reload. CPU/RAM/Disk load are refreshed
    using an ajax request every second. (Could use websockets, but kind of overkill there)
    """
    flash_default_password()
    app.sysinfo.update()
    return render_template("sysinfo.html", sysinfo=app.sysinfo, active_page="sysinfo")


@app.route('/help', methods=['GET'])
def help():
    """
    Help page. Contains the FAQ.
    """
    flash_default_password()
    return render_template("help.html", active_page="help")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login. Also the page set for flask_login as the redirect for the login_required decorator.
    """
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
    """
    Logouts the user and removes the password hash from the session.
    """
    logout_user()
    PasswordManager.pop_session_pwdh()
    return redirect(url_for('login'))
