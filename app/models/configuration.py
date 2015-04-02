# -*- coding: utf-8 -*-

from app import app, db

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

    risks = db.relationship('Risk', secondary=configuration_risks, backref=db.backref('configurations', lazy='dynamic'))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

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
        return self.path

    # Intermediate vuln table
configurationvalues_vulnbasic = db.Table(
    'configurationvalues_vulnbasic',
    db.Column('configurationvalues_id', db.Integer, db.ForeignKey('configurationvalues.id')),
    db.Column('vulnbasic_id', db.Integer, db.ForeignKey('vulnbasic.id')),
    )
    
configurationvalues_vulnperm = db.Table(
    'configurationvalues_vulnperm',
    db.Column('configurationvalues_id', db.Integer, db.ForeignKey('configurationvalues.id')),
    db.Column('vulnperm_id', db.Integer, db.ForeignKey('vulnperm.id')),
    )
    
configurationvalues_vulncve = db.Table(
    'configurationvalues_vulncve',
    db.Column('configurationvalues_id', db.Integer, db.ForeignKey('configurationvalues.id')),
    db.Column('vulncve_id', db.Integer, db.ForeignKey('vulncve.id')),
    )

class ConfigurationValues(db.Model):
    """ 
    Represents value from config file
    """
    __tablename__='configurationvalues'    
    friendly_name="Configuration Values"
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(15))
    model = db.Column(db.String(20))
    uptime = db.Column(db.String(50))
    configuration_id = db.Column(db.Integer(), db.ForeignKey('configuration.id'))
    
    # Vulnerability fields
    vulncve = db.relationship('VulnCve', secondary=configurationvalues_vulncve, backref=db.backref('configurations', lazy='dynamic'))
    vulnbasic = db.relationship('VulnBasic', secondary=configurationvalues_vulnbasic, backref=db.backref('configurations', lazy='dynamic'))
    vulnperm = db.relationship('VulnPerm', secondary=configurationvalues_vulnperm, backref=db.backref('configurations', lazy='dynamic'))
    
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


