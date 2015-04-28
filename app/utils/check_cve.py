# -*- coding: utf-8 -*-

import re
import datetime
from app import db, app
from app.models import Device, Configuration, ConfigurationValues, VulnCve, ConfVuln


def checkcve_all():
    for device in Device.query.all():
        checkcve(device)
    db.session.commit()


def checkcve(device, single=False):
    date = datetime.date.today()
    for config in Configuration.query.filter(Configuration.device == device):
        ver_search = re.search('version\.txt', config.path)
        if ver_search:
            for values in ConfigurationValues.query.filter(ConfigurationValues.configuration == config):
                dev_version = values.version
                for cve in VulnCve.query.filter(not VulnCve.version == ''):
                    cve_vers = cve.version
                    inf = ''
                    sep = ''
                    sup = ''
                    cvevers_search = re.search(
                        '(\d+\.\d)(?:([-,])(\d+\.\d))?', cve_vers)
                    if cvevers_search:
                        if cvevers_search.group(1):
                            inf = cvevers_search.group(1)
                            obj = ConfVuln()
                        if cvevers_search.group(2):
                            sep = cvevers_search.group(2)
                        if cvevers_search.group(3):
                            sup = cvevers_search.group(3)

                        app.logger.debug('DEBUG: ' + cve.version)
                        if sep and sep == ',':
                            if dev_version in [inf, sup]:
                                obj.configuration_id = config.id
                                obj.vulncve_id = cve.id
                        if sep and sep == '-':
                            if inf <= dev_version <= sup:
                                obj.configuration_id = config.id
                                obj.vulncve_id = cve.id
                        else:
                            app.logger.debug('Device version: ' + dev_version + ' ## Cve version: ' + inf)
                            if dev_version == inf:
                                obj.configuration_id = config.id
                                obj.vulncve_id = cve.id
                        if obj.vulncve_id:
                            obj.date=date
                            db.session.add(obj)
    if single:
        db.session.commit()
