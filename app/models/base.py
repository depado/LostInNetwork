# -*- coding: utf-8 -*-

from app import db, app


class DbMixin(object):

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            message = "Error during save operation"
            app.logger.error("{} : {}".format(message, e))
            app.logger.exception(message)
            db.session.rollback()
            return False
        return True

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except Exception as e:
            message = "Error during delete operation"
            app.logger.error("{} : {}".format(message, e))
            app.logger.exception(message)
            db.session.rollback()
            return False
        return True
