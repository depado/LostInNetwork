# -*- coding: utf-8 -*-

import redis
import celery
import re
import os
from datetime import datetime

from app import app, db
from app.models import Device, Configuration, VulnBasic, ConfVuln

ANALYSE_KEY = "analyse_task_uuid"
ANALYSE_LOCK = redis.Redis().lock("celery_analyse_lock")

CISCO_PRECO_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "csv", "preco.csv")

@celery.task(bind=True)
def async_analysis(self):
    have_lock = False
    try:
        app.logger.info("Started Analysis")
        have_lock = ANALYSE_LOCK.acquire(blocking=False)
        today = datetime.now()
        for d in Device.query.all():
            for conf in Configuration.query.filter(Configuration.path.like('%run.txt')).filter(Configuration.device == d).order_by(Configuration.date.desc()).limit(1):
                value = ""
                for v in VulnBasic.query.all():
                    pattern = re.compile(v.match)
                    for i, line in enumerate(open(conf.path)):
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
            #for conf in Configuration.query.filter(Configuration.path.like('%version.txt')).filter(Configuration.device == d).order_by(Configuration.date.desc()).limit(1):


        db.session.commit()
    finally:
        if have_lock:
            ANALYSE_LOCK.release()
