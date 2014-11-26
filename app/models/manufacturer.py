# -*- coding: utf-8 -*-

from app import db


class Manufacturer(db.Model):
    """
    Represents a Manufacturer of a DeviceType
    Example : Cisco
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
