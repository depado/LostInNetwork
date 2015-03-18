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
        run_configuration=Configuration(path=run_file,device=device)
        route_configuration=Configuration(path=route_file,device=device)
        run_configuration.save()
        route_configuration.save()
        for lines in open(run_file):
            lines=lines.strip()
            version_Search=re.search('(?i)version\s(.*)',lines)
            if version_Search:
                run_version=version_Search.group(1)
                run_configurationValue=ConfigurationValues(version=run_version,configuration_id=configurationvalues.id)
                run_configurationValue.save()
#                print ("version :"+ version)
#            interface_Search=re.search('(?i)interface\s(.*)',lines)
#            if interface_Search:
#                interface=interface_Search.group(1)
#                print ("interface : "+ interface)

if __name__ == '__main__':
                    main()

