# -*- coding: utf-8 -*-
import re
from app.models import Device, Configuration, ConfigurationValues, ConfVuln, VulnBasic, VulnCve 
import datetime

def mainanalyse():
    jour=datetime.datetime.now()
    for conf in Configuration.query.all():
        value=""
        runpath = re.compile('.*run.txt')
        crun = runpath.match(conf.path)
        for v in VulnBasic.query.all():
            pattern=re.compile(v.match)
            if crun:
                for i, line in enumerate(open(conf.path)):
                    if (re.match(pattern, line) and v.expectmatch==0):
                        value='ERROR : %s-%s found on line %s - file %s' % (pattern, v.expectmatch, i+1, conf.path)
                        ConfVuln(vulnbasic_id=v.id,configuration_id=conf.id).save()
                    elif (re.match(pattern, line) and v.expectmatch==1):
                        value='%s-%s found on line %s - file %s' % (pattern, v.expectmatch, i+1, conf.path)
                if (not value and v.expectmatch==1):
                    ConfVuln(vulnbasic_id=v.id,configuration_id=conf.id).save()
                value=""


