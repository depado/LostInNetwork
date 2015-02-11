# -*- coding: utf-8 -*-

from app import app, db


class Manufacturer(db.Model):
    """
    Represents a Manufacturer of a DeviceType
    Example : Cisco
    """
    friendly_name = "Manufacturer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    devicetypes = db.relationship('DeviceType', backref='manufacturer', lazy='dynamic')

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error("Error during save operation {}".format(e))
            app.logger.exception()
            db.session.rollback()
            return False
        return True

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error("Error during delete operation {}".format(e))
            app.logger.exception()
            db.session.rollback()
            return False
        return True

    def __repr__(self):
        return self.name
