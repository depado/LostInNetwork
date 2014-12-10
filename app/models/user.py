# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class Permission(object):
    allowed = "A"
    denied = "D"
    restricted = "R"


class User(db.Model):
    """
    A simple user model with permission handling and password hash.
    Implements two methods to set the password and check the password.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(54))
    permission = db.Column(db.String(1))
    superuser = db.Column(db.Boolean())
    active = db.Column(db.Boolean())

    def __init__(self, username, password, superuser=False, active=False):
        self.username = username
        self.set_password(password)
        self.permission = Permission.allowed
        self.active = active
        self.superuser = superuser

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return False
        return True

    def is_authenticated(self):
        return True

    def is_superuser(self):
        return self.superuser

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
            return str(self.id)

    def __repr__(self):
        return "<User %r>" % self.username

    def __unicode__(self):
        return "<User %r>" % self.login


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)
