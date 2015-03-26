#!/usr/bin/python3
# Version 1.0
# Author hiziv
from app import app
from app import db
from app.models.device import Device
from app.models.configuration import Configuration
from app.models.configuration import ConfigurationValues
import re

def main():
    for device in Device.query.all():
        run_file="data/" + device.name + "-run.txt"
        route_file="data/" + device.name + "-route.txt"
        route_configuration=Configuration(path=route_file,device=device)
        try:
            run_configuration=Configuration(path=run_file,device=device)
            run_configuration.save()
            route_configuration.save()
        except:
            continue 
            #run_configuration.delete()
            #run_configuration.save()
            #route_configuration.delete()
            #route_configuration.save()
    for conf in Configuration.query.all():            
        for lines in open(conf.path):
            lines=lines.strip()
            version_Search=re.search('(?i)version\s(.*)',lines)
            if version_Search:
                run_version=version_Search.group(1)
                run_configurationValue=ConfigurationValues(version=run_version,configuration_id=conf.id)
                try:
                    run_configurationValue.save()
                except:
                    continue
#            interface_Search=re.search('(?i)interface\s(.*)',lines)
#            if interface_Search:
#                interface=interface_Search.group(1)
#                print ("interface : "+ interface)

if __name__ == '__main__':
    main()

