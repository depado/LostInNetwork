# -*- coding: utf-8 -*-

import re

from app.models import Device, Configuration, ConfigurationValues, DeviceInterfaces, DeviceRoutes
from app.models import routeCisco

def mainupdate():
    for d in Device.query.all():
        for c in d.configurations:
            c.delete()
        run_file = "data/config/" + d.name + "-run.txt"
        route_file = "data/config/" + d.name + "-route.txt"
        version_file = "data/config/" + d.name + "-version.txt"
        run_configuration = Configuration(path=run_file, device=d)
        route_configuration = Configuration(path=route_file, device=d)
        version_configuration = Configuration(path=version_file, device=d)
        run_configuration.save()
        route_configuration.save()
        version_configuration.save()
    runpath = re.compile('.*run.txt')
    routepath = re.compile('.*route.txt')
    versionpath = re.compile('.*version.txt')

    # Ouais ok je delete tout, mais on n'a pas vraiment le choix et je vous emmerde
    for c in ConfigurationValues.query.all():
        c.delete()
    for c in DeviceInterfaces.query.all():
        c.delete()
    for c in DeviceRoutes.query.all():
        c.delete()

    for conf in Configuration.query.all():
        cversion = versionpath.match(conf.path)
        crun = runpath.match(conf.path)
        croute = routepath.match(conf.path)
        if cversion:
            for lines in open(conf.path):
                lines = lines.strip()
                cisco_search = re.search('(?i)Cisco\sIOS.*,.*\((\w+\d*)-.*\).*Version\s(\d*.\d*)\(.*', lines)
                if cisco_search:
                    model_version = cisco_search.group(1)
                    version_version = cisco_search.group(2)
                    ConfigurationValues(version=version_version, model=model_version, configuration=conf).save()
        if crun:
            int_regex = re.compile('(?i)interface\s(.*)\n ip address (.*) (.*)\n.*\n (?!shutdown)', re.MULTILINE)
            with open(conf.path) as runfile:
                for match in int_regex.finditer(runfile.read()):
                    interface_run = match.group(1)
                    ip_run = match.group(2)
                    mask_run = match.group(3)
                    DeviceInterfaces(name=interface_run, addr=ip_run, netmask=mask_run, configuration_id=conf.id).save()
        if croute:
            routeCisco(croute, conf.id)
#            routeregex = re.compile('\w\**\s*(\d+.\d+.\d+.\d+)/*(\d+)*.*(connected|via),*\s+(.*)', re.MULTILINE)
#            with open(conf.path) as runfile:
#                for match in routeregex.finditer(runfile.read()):
#                    net_route = match.group(1)
#                    mask_route = match.group(2)
#                    gw_route = match.group(4)
#                    if match.group(3)=="connected":
#                        conn_route = 1
#                    else:
#                        conn_route = 0
#                    DeviceRoutes(net_dst=net_route, net_mask=mask_route, gw=gw_route, connected=conn_route, configuration_id=conf.id).save()

