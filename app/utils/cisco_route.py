# -*- coding: utf-8 -*-

import re
import time
import datetime
from app import db
from app.models import Device, DeviceRoutes 

def routeCisco (ROUTE_FILE, CONF_ID):
    #ROUTE_FILE = 'data/rtr3-route.txt'
    print('DEBUG: ' + ROUTE_FILE)
    print('DEBUG: ' + str(CONF_ID))
    IPMATCH = '(?:\d{1,3}\.){1,3}\d{1,3}'
    nbr_subnet = 0
    mask = 0 
    DIRECTLY= "^(\w)\*?\s+((?:\d{1,3}\.){1,3}\d{1,3})(?:\/(\d+))? is directly.*, (\S+)$"
    VIA = "^(\w)\*?\s+((?:\d{1,3}\.){1,3}\d{1,3})(?:\/(\d+))? \[.*\] via (\S+)$"
    with open(ROUTE_FILE, 'r') as f:
        for line in f:
            line=line.strip()
            g =re.search('^Gateway.*$', line)
            route_search = re.search('(?:\d{1,3}\.){1,3}\d{1,3}(?:\/\d+)?', line)

            if g:
                continue
#            print(line) 
            if route_search:
                sub_search = re.search('^.*\/(\d+) is subnetted, (\d+)', line)
                if sub_search:
                    mask = sub_search.group(1)
                    nbr_subnet = int(sub_search.group(2))
                    continue

                if nbr_subnet > 0 :
                    dir_search = re.search(DIRECTLY, line)
                    if dir_search:
                        connect = dir_search.group(1)
                        network = dir_search.group(2)
                        if dir_search.group(3):
                            netmask = dir_search.group(3)
                        gw = dir_search.group(4)
                        nbr_subnet -= 1

                    via_search = re.search(VIA, line)
                    if via_search:
                        connect = via_search.group(1)
                        network = via_search.group(2)
                        if dir_search.group(3):
                            netmask = dir_search.group(3)
                        gw = via_search.group(4)
                        nbr_subnet -= 1

                dir_search = re.search(DIRECTLY, line)
                if dir_search:
                    connect = dir_search.group(1)
                    network = dir_search.group(2)
                    netmask = dir_search.group(3)
                    gw = dir_search.group(4)

                via_search = re.search(VIA, line)
                if via_search:
                    connect = via_search.group(1)
                    network = via_search.group(2)
                    netmask = via_search.group(3)
                    gw = via_search.group(4)
                
                route = DeviceRoutes()
                route.net_dst = network
                # FIXME: python error: column netmas seems does not exist in
                # deviceroute table 
                print('DEBUG mask: ' + str(netmask))
                if netmask == None:
                    route.net_mask = str(mask)
                else:
                    route.net_mask = str(netmask)
                route.gw = gw
                route.status = connect 
                route.configuration_id = CONF_ID
                db.session.add(route)
                print('DEBUG: add value to object')

    db.session.commit()
    print('DEBUG: Commit')
