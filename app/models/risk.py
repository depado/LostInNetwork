# -*- coding: utf-8 -*-

from app import app, db


class RiskType(db.Model):
    """
    Represents a Risk Type
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

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


class RiskLevel(db.Model):
    """
    Represents a Risk Level on a scale of 10
    """
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Enum('0','1','2','3','4','5','6','7','8','9','10', name='level_id'), default='0')

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


class Risk(db.Model):
    """
    Represents a risk.
    A risk can be associated with multiple devices and configurations
    """
    id = db.Column(db.Integer, primary_key=True)
    risklevel_id = db.Column(db.Integer, db.ForeignKey('risk_level.id'))
    risktype_id = db.Column(db.Integer, db.ForeignKey('risk_type.id'))

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

