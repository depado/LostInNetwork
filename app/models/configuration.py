# -*- coding: utf-8 -*-

from app import db

configuration_risks = db.Table(
    'configuration_risks',
    db.Column('configuration_id', db.Integer, db.ForeignKey('configuration.id')),
    db.Column('risk_id', db.Integer, db.ForeignKey('risk.id')),
)


class Configuration(db.Model):
    """
    Represents a Configuration file
    """
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), unique=True)

    risks = db.relationship('Risk', secondary=configuration_risks, backref=db.backref('configurations', lazy='dynamic'))
