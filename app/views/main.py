# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request

from flask_login import login_user, logout_user, current_user, login_required

from app import app
from app.forms import LoginForm
from app.models import User


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        return redirect(url_for('index'))
    else:
        return render_template("login.html", form=form)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))
