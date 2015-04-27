# -*- coding: utf-8 -*-

import re
from app import db, app
from app.models import DeviceRoutes


def routeCisco (ROUTE_FILE, CONF_ID):
    # ROUTE_FILE = 'data/rtr3-route.txt'
    print('DEBUG: ' + ROUTE_FILE)
    print('DEBUG: ' + str(CONF_ID))
    # IPMATCH = '(?:\d{1,3}\.){1,3}\d{1,3}'
    nbr_subnet = 0
    mask = 0 
    DIRECTLY= "^(\w)\*?\s+((?:\d{1,3}\.){1,3}\d{1,3})(?:\/(\d+))? is directly.*, (\S+)$"
    VIA = "^(\w)\*?\s+((?:\d{1,3}\.){1,3}\d{1,3})(?:\/(\d+))? \[.*\] via (\S+)$"
    with open(ROUTE_FILE) as f:
        for line in f:
            line=line.strip()
            g =re.search('^Gateway.*$', line)
            route_search = re.search('(?:\d{1,3}\.){1,3}\d{1,3}(?:\/\d+)?', line)

            if g:
                continue
            if route_search:
                sub_search = re.search('^.*\/(\d+) is subnetted, (\d+)', line)
                if sub_search:
                    mask = sub_search.group(1)
                    nbr_subnet = int(sub_search.group(2))
                    continue

                if nbr_subnet > 0 :
                    dir_search = re.search(DIRECTLY, line)
                    via_search = re.search(VIA, line)
                    if dir_search or via_search:
                        search = dir_search if dir_search else via_search
                        connect = search.group(1)
                        network = search.group(2)
                        if search.group(3):
                            netmask = search.group(3)
                        gw = search.group(4)
                        nbr_subnet -= 1

                dir_search = re.search(DIRECTLY, line)
                via_search = re.search(VIA, line)
                if dir_search or via_search:
                    search = dir_search if dir_search else via_search
                    connect = search.group(1)
                    network = search.group(2)
                    netmask = search.group(3)
                    gw = search.group(4)

                route = DeviceRoutes()
                route.net_dst = network
                # FIXME: python error: column netmas seems does not exist in
                app.logger.debug('Mask: ' + str(netmask))
                if netmask is None:
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
