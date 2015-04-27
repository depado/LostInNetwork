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

@manager.command
def create_superuser():
    """
    TODO: Take some inputs to define username and password for the superuser instead of forcing root/root
    """
    from app.models import User
    user = User(username='root', password='root', active=True, superuser=True)
    user.save()

@manager.command
def create_test_data():
    from app.models import User, Manufacturer, DeviceType, Lan
    user = User(username='root', password='root', active=True, superuser=True)
    user.save()
    m = Manufacturer(name="Cisco")
    m.save()
    d = DeviceType(manufacturer=m, category="Router", name="Cisco Router")
    d.save()
    l = Lan(name='test')
    l.save()

if __name__ == '__main__':
    manager.run()
