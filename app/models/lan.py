# -*- coding: utf-8 -*-

from app import db

from .base import DbMixin


class Lan(db.Model, DbMixin):
    """
    Represents a Lan
    """
    friendly_name = "Lan"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    devices = db.relationship('Device', backref='lan', lazy='dynamic')

    def __repr__(self):
        return self.name
