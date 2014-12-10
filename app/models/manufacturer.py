# -*- coding: utf-8 -*-

from app import db


class Manufacturer(db.Model):
    """
    Represents a Manufacturer of a DeviceType
    Example : Cisco
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    devicetypes = db.relationship('DeviceType', backref='manufacturer', lazy='dynamic')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return self.name
