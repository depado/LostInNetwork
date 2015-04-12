# -*- coding: utf-8 -*-

from app import db

from .base import DbMixin


class Manufacturer(db.Model, DbMixin):
    """
    Represents a Manufacturer of a DeviceType
    Example : Cisco
    """
    friendly_name = "Manufacturer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    devicetypes = db.relationship('DeviceType', backref='manufacturer', lazy='dynamic')

    def __repr__(self):
        return self.name
