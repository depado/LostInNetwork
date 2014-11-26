# -*- coding: utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app
from app import db

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def create_db():
    db.create_all()
    from app.models import User
    user = User(username='root', password='root', active=True, superuser=True)
    user.save()


if __name__ == '__main__':
    manager.run()
