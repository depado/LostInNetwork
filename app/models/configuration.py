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
    friendly_name = "Configuration"

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), unique=True)

    devices = db.relationship('Device', backref='configuration', lazy='dynamic')
    risks = db.relationship('Risk', secondary=configuration_risks, backref=db.backref('configurations', lazy='dynamic'))

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return False
        return True

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return False
        return True

    def __repr__(self):
        return self.path
