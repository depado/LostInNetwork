#!/usr/bin/python3
# Version 1.0
# Author hiziv
from app import app
from app import db
from app.models.device import Device
from app.models.configuration import Configuration
from app.models.configuration import ConfigurationValues
from app.models.device import DeviceInterfaces, DeviceRoutes
import re

def mainupdate():
    for d in Device.query.all():
        for c in d.configurations:
            c.delete()
        run_file="data/" + d.name + "-run.txt"
        route_file="data/" + d.name + "-route.txt"
        version_file="data/" + d.name + "-version.txt"
        run_configuration=Configuration(path=run_file,device=d)
        route_configuration=Configuration(path=route_file,device=d)
        version_configuration=Configuration(path=version_file,device=d)
        run_configuration.save()
        route_configuration.save()
    runpath=re.compile('.*run.txt')
    routepath=re.compile('.*route.txt')
    versionpath=re.compile('.*version.txt')
          
    #Ouais ok je delete tout, mais on a pas vraiment le choix et je vous emmerde
    for c in ConfigurationValues.query.all():
        c.delete()            
    for c in DeviceInterfaces.query.all():
        c.delete() 
    for c in DeviceRoutes.query.all():
        c.delete()
         
    for conf in Configuration.query.all():
        cversion=versionpath.match(conf.path)
        crun=runpath.match(conf.path)
        croute=routepath.match(conf.path)
        if cversion:
            for lines in open(conf.path):
                lines=lines.strip()
                Cisco_Search=re.search('(?i)Cisco\sIOS.*,.*\((\w+\d*)-.*\).*Version\s(\d*.\d*)\(.*',lines)
                if Cisco_Search:
                    model_version=Cisco_Search.group(1)
                    version_version=Cisco_Search.group(2)
                    version_configurationValue=ConfigurationValues(version=version_version,model=model_version,configuration_id=conf.id)
                    version_configurationValue.save()
        if crun:
            IntRegex=re.compile('(?i)interface\s(.*)\n ip address (.*) (.*)\n.*\n (?!shutdown)',re.MULTILINE)
            runfile=open(conf.path, 'r')
            text=runfile.read()
            for match in IntRegex.finditer(text):
                interface_run=match.group(1)
                ip_run=match.group(2)
                mask_run=match.group(3)
                run_deviceInterfaces=DeviceInterfaces(name=interface_run,addr=ip_run,netmask=mask_run,configuration_id=conf.id)
                run_deviceInterfaces.save()
        if croute:
            RouteRegex=re.compile('\w\*+\s*(\d+.\d+.\d+.\d+/\d+).*via\s+(.*)',re.MULTILINE)
            runfile=open(conf.path, 'r')
            text=runfile.read()
            for match in RouteRegex.finditer(text):
                net_route=match.group(1)
                gw_route=match.group(2)
                route_deviceRoutes=DeviceRoutes(net_dst=net_route,gw=gw_route,configuration_id=conf.id)
                route_deviceRoutes.save()

if __name__ == '__main__':
    main()

