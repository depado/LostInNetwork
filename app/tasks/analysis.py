# -*- coding: utf-8 -*-

import redis
import celery
import re
import os
import time
from datetime import datetime

from app import app, db
from app.models import Device, Configuration, VulnBasic, ConfVuln, ConfigurationValues, VulnCve
from app.utils.crypto import PasswordManager

ANALYSE_KEY = "analyse_task_uuid"
ANALYSE_LOCK = redis.Redis().lock("celery_analyse_lock")

CISCO_PRECO_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "csv", "preco.csv")


@celery.task(bind=True)
def async_analysis(self, pwdh):
    have_lock = False
    try:
        app.logger.info("Started Analysis")
        have_lock = ANALYSE_LOCK.acquire(blocking=False)
        if VulnBasic.query.count() == 0:
            app.logger.info("VulnBasic table is empty, adding the preco")
            list_preco = open(CISCO_PRECO_FILE).readlines()
            for i in list_preco:
                x = i.split(';')
                preco = VulnBasic(match=(x[0]), expectmatch=(x[1]), description=(x[2]))
                db.session.add(preco)
            db.session.commit()
        total = Device.query.count()
        self.update_state(state='PROGRESS', meta={'message': "Started Analysis for {total} device{total_plural}".format(
            total=total,
            total_plural="s" if total > 1 else "",
        ), 'percentage': 5})
        done = 0
        today = datetime.now()
        for d in Device.query.all():
            for conf in Configuration.query.filter(Configuration.path.like('%run%.txt')).filter(Configuration.device_id == d.id).order_by(Configuration.date.desc()).limit(1):
                value = ""
                for v in VulnBasic.query.all():
                    pattern = re.compile(v.match)
                    for i, line in enumerate(PasswordManager.decrypt_file_content(conf.path, pwdh).split('\n')):
                        if re.match(pattern, line) and v.expectmatch == 0:
                            value = 'ERROR : %s-%s found on line %s - file %s' % (pattern, v.expectmatch, i + 1,
                                                                                  conf.path)
                            vuln_values = ConfVuln()
                            vuln_values.vulnbasic_id = v.id
                            vuln_values.configuration_id = conf.id
                            vuln_values.date = today
                            db.session.add(vuln_values)
                        elif re.match(pattern, line) and v.expectmatch == 1:
                            value = '%s-%s found on line %s - file %s' % (pattern, v.expectmatch, i + 1, conf.path)
                    if not value and v.expectmatch == 1:
                        vuln_values = ConfVuln()
                        vuln_values.vulnbasic_id = v.id
                        vuln_values.configuration_id = conf.id
                        vuln_values.date = today
                        value = ""
                        db.session.add(vuln_values)
            for conf in Configuration.query.filter(Configuration.path.like('%version%.txt')).filter(Configuration.device_id == d.id).order_by(Configuration.date.desc()).limit(1):
                for line in PasswordManager.decrypt_file_content(conf.path, pwdh).split('\n'):
                    cisco_search = re.search('(?i)Cisco\sIOS.*,.*\((\w+\d*)-.*\).*Version\s(\d*.\d*)\(.*', line)
                    if cisco_search:
                        version_values = ConfigurationValues()
                        version_values.version = cisco_search.group(2)
                        version_values.model = cisco_search.group(1)
                        version_values.configuration_id = conf.id
                        db.session.add(version_values)

                for value in ConfigurationValues.query.filter(ConfigurationValues.configuration_id == conf.id):
                    dev_version = value.version
                    for cve in VulnCve.query.filter(not VulnCve.version == ''):
                        cve_vers = cve.version
                        inf = ''
                        sep = ''
                        sup = ''
                        cvevers_search = re.search('(\d+\.\d)(?:([-,])(\d+\.\d))?', cve_vers)
                        if cvevers_search:
                            if cvevers_search.group(1):
                                inf = cvevers_search.group(1)
                                obj = ConfVuln()
                            if cvevers_search.group(2):
                                sep = cvevers_search.group(2)
                            if cvevers_search.group(3):
                                sup = cvevers_search.group(3)
                            if sep and sep == ',':
                                if dev_version in [inf, sup]:
                                    obj.configuration_id = conf.id
                                    obj.vulncve_id = cve.id
                            if sep and sep == '-':
                                if inf <= dev_version <= sup:
                                    obj.configuration_id = conf.id
                                    obj.vulncve_id = cve.id
                            else:
                                if dev_version == inf:
                                    obj.configuration_id = conf.id
                                    obj.vulncve_id = cve.id
                            if obj.vulncve_id:
                                obj.date = today
                                db.session.add(obj)
            done += 1
            self.update_state(
                state='PROGRESS',
                meta={'message': "Done {done} device{done_plural} over {total} device{total_plural}".format(
                    done=done,
                    done_plural="s" if done > 1 else "",
                    total=total,
                    total_plural="s" if total > 1 else ""
                ), 'percentage': done/total*100-1})
        db.session.commit()
        app.logger.info("Finished Analysis")
        self.update_state(state='PROGRESS', meta={'message': "Analysis Finished", 'percentage': 100})
        time.sleep(5)
    finally:
        if have_lock:
            ANALYSE_LOCK.release()
