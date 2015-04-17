# -*- coding: utf-8 -*-

import logging
import re
from logging.handlers import RotatingFileHandler

from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask
from jinja2 import evalcontextfilter, Markup, escape

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

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.config_from_object('app.tasks.beat_config')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import models, views

from app.utils import SystemInformation
app.sysinfo = SystemInformation()

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
