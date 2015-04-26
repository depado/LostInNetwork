# -*- coding: utf-8 -*-

import re
import time
import datetime
from app import db
from app.models import Device, Configuration, ConfigurationValues, DeviceInterfaces, DeviceRoutesi
from app.utils import routeCisco
from sqlalchemy import desc

def mainupdate():
    today = datetime.date.today()
    for c in Configuration.query.all():
        c.delete()
    for c in ConfigurationValues.query.all():
        c.delete()
    for c in DeviceInterfaces.query.all():
        c.delete()
    for c in DeviceRoutes.query.all():
        c.delete()
    for d in Device.query.all():
        run_file = "data/devices/" + d.name + "-run.txt"
        route_file = "data/devices/" + d.name + "-route.txt"
        version_file = "data/devices/" + d.name + "-version.txt"
        run_configuration=Configuration()
        run_configuration.path=run_file
        run_configuration.device=d
        run_configuration.date=today
        route_configuration=Configuration()
        route_configuration.path=route_file
        route_configuration.device=d
        route_configuration.date=today
        version_configuration=Configuration()
        version_configuration.path=version_file
        version_configuration.device=d
        version_configuration.date=today

    runpath = re.compile('.*run.txt')
    routepath = re.compile('.*route.txt')
    versionpath = re.compile('.*version.txt')
    for d in Device.query.all():
        for conf in Configuration.query.filter(Configuration.path.like('%version.txt')).filter(Configuration.device_id==d.id).order_by(Configuration.date.desc()).limit(1):
            for lines in open(conf.path):
                lines = lines.strip()
                cisco_search = re.search('(?i)Cisco\sIOS.*,.*\((\w+\d*)-.*\).*Version\s(\d*.\d*)\(.*', lines)
                if cisco_search:
                    version_values=ConfigurationValues()
                    version_values.version=cisco_search.group(2)
                    version_values.model=cisco_search.group(1)
                    version_values.configuration_id=conf.id
                    db.session.add(version_values)

        for conf in Configuration.query.filter(Configuration.path.like('%route.txt')).filter(Configuration.device_id==d.id).order_by(Configuration.date.desc()).limit(1):
            routeCisco( conf.path, conf.id)

    db.session.commit()
