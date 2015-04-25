# -*- coding: utf-8 -*-
import pdb
import re
from app.models import Device, Configuration, ConfigurationValues, ConfVuln, VulnBasic, VulnCve 


def mainanalyse():
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
                     #   print (value)
                if (not value and v.expectmatch==1):
                    #print('%s-%s not found on %s' % (pattern, v.expectmatch, conf.path))
                    ConfVuln(vulnbasic_id=v.id,configuration_id=conf.id).save()
                value=""


