# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask

from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)

handler = RotatingFileHandler(app.config.get('LOG_FILE'), maxBytes=10000, backupCount=5)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt='%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s',
    datefmt='%b %d %H:%M:%S'
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import models, views

from app.utils import SystemInformation
app.sysinfo = SystemInformation()
