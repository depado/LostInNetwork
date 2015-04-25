# -*- coding: utf-8 -*-

import re
import time
import datetime
from app import db
from app.models import Device, Configuration, ConfigurationValues, VulnCve, ConfVuln


def checkcve():
    date = datetime.date.today()
    dev_name = 'rtr1'
    for dev in Device.query.filter(Device.name == dev_name):
        for config in Configuration.query.filter(Configuration.device_id == dev.id):
            ver_search = re.search('version\.txt', config.path)
            if ver_search:
                config_id = config.id
                for values in ConfigurationValues.query.filter(
                        ConfigurationValues.configuration_id == config_id):
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
                                #print('DEBUG inf: ' + str(inf))
                            if cvevers_search.group(2):
                                sep = cvevers_search.group(2)
                                #print('DEBUG sep: ' + sep)
                            if cvevers_search.group(3):
                                sup = cvevers_search.group(3)
                                #print('DEBUG sup: ' + sup)

                            print('DEBUG: ' + cve.version)
                            # Compare device version with cve version
                            if sep and sep == ',':
                                #printi('virgule')
                                if dev_version == inf:
                                    #print('yeah inf')
                                    obj.configuration_id = config.id
                                    obj.vulncve_id = cve.id
                                elif dev_version == sup:
                                    obj.configuration_id = config.id
                                    obj.vulncve_id = cve.id
                                    #print('yeah sup')
                            if sep and sep == '-':
                                #print('tiret')
                                if dev_version >= inf and dev_version <= sup:
                                    obj.configuration_id = config.id
                                    obj.vulncve_id = cve.id
                            else:
                                #print('no separator')
                                print('Device version: ' + dev_version + ' ## Cve version: ' + inf)
                                if dev_version == inf:
                                    #print('Yeah ca match')
                                    obj.configuration_id = config.id
                                    obj.vulncve_id = cve.id
                            if obj.vulncve_id:
                                obj.date=date
                                db.session.add(obj)
    db.session.commit()
