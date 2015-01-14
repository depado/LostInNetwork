# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask

from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import views, models
