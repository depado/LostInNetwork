# -*- coding: utf-8 -*-

from app import db


class RiskType(db.Model):
    """
    Represents a Risk Type
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


class RiskLevel(db.Model):
    """
    Represents a Risk Level on a scale of 10
    """
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Enum('1','2','3','4','5','6','7','8','9','10', name='level_id'))


class Risk(db.Model):
    """
    Represents a risk.
    A risk can be associated with multiple devices and configurations
    """
    id = db.Column(db.Integer, primary_key=True)
    risklevel_id = db.Column(db.Integer, db.ForeignKey('risk_level.id'))
    risktype_id = db.Column(db.Integer, db.ForeignKey('risk_type.id'))

