# -*- coding: utf-8 -*-
import re
from app.models import Device, Configuration, ConfVuln, VulnBasic
import datetime
from app import db

def mainanalyse():
    today=datetime.datetime.now()
    for d in Device.query.all():
        for conf in Configuration.query.filter(Configuration.path.like('%run.txt')).filter(Configuration.device==d).order_by(Configuration.date.desc()).limit(1):
            value = ""
            for v in VulnBasic.query.all():
                pattern=re.compile(v.match)
                for i, line in enumerate(open(conf.path)):
                    if (re.match(pattern, line) and v.expectmatch==0):
                        value='ERROR : %s-%s found on line %s - file %s' % (pattern, v.expectmatch, i+1, conf.path)
                        vuln_values=ConfVuln()
                        vuln_values.vulnbasic_id = v.id
                        vuln_values.configuration_id = conf.id
                        vuln_values.date = today
                    elif (re.match(pattern, line) and v.expectmatch==1):
                        value='%s-%s found on line %s - file %s' % (pattern, v.expectmatch, i+1, conf.path)
                if not value and v.expectmatch==1:
                    vuln_values=ConfVuln()
                    vuln_values.vulnbasic_id = v.id
                    vuln_values.configuration_id = conf.id
                    vuln_values.date = today
                    value=""
                db.session.add(vuln_values)
    
        db.session.commit()


