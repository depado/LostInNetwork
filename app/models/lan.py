# -*- coding: utf-8 -*-

from app import db


class Lan(db.Model):
    """
    Represents a Lan
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    devices = db.relationship('Device', backref='lan', lazy='dynamic')
