# -*- coding: utf-8 -*-

import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE_DIR = os.path.join(CURRENT_DIR, "database")
LOG_DIR = os.path.join(CURRENT_DIR, "log")
LOG_FILE = os.path.join(LOG_DIR, 'lostinnetwork.log')
DATA_DIR = os.path.join(CURRENT_DIR, "data")

REQUIRED_FOLDERS = {
    'Data': DATA_DIR,
    'Log': LOG_DIR,
    'Database': DATABASE_DIR
}


def check_create_necessary_folders():
    for name, path in REQUIRED_FOLDERS.items():
        if not os.path.exists(path):
            print("{} folder not found. Creating.".format(name))
            os.makedirs(path)


def touch(fullpath):
    with open(fullpath, 'a'):
        pass


def check_create_files_folders():
    check_create_necessary_folders()
    if not os.path.exists(LOG_FILE):
        print("Log file not found. Creating.")
        touch(LOG_FILE)


check_create_files_folders()

from app import app
from app import db

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def init():
    import getpass
    from app.models import User, Manufacturer, DeviceType, Lan

    try:
        print("Creating the database...")
        db.create_all()
        print("Enter the credentials for the main user :")
        print("Username : ", end="")
        usr = input()
        pwd = getpass.getpass()
        user = User(username=usr, password=pwd, active=True, superuser=True)
        user.save()
        m = Manufacturer(name="Cisco")
        m.save()
        DeviceType(manufacturer=m, category="Router", name="Cisco Router").save()
        l = Lan(name='test')
        l.save()
        print("Done. Successfully added the main user, and the Cisco Router device type.")
        print("You can now start the application using manage.py runserver for test purpose. ")
    except Exception as e:
        print("An error occured ! Error was : {}".format(e))


if __name__ == '__main__':
    manager.run()
