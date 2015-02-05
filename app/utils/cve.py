# -*- coding: utf-8 -*-


from app import app
from app import db
from app.models.vuln import VulnCve
from flask import session
from sqlalchemy import Table, MetaData, create_engine, select, cast
import gzip
import logging
import os
import re
import tempfile
import urllib.request

def startLog():
    global log,logvar
    uid=os.getlogin()
    logvar={'user' : uid }
    # Print log with same format as default syslog
    logformat='%(asctime)s %(user)s %(name)s[%(process)d] %(levelname)s %(message)s'
    log=logging.getLogger('LOSTINNETWORK')
    logging.basicConfig(filename=app.config.get('LOG_FILE'),format=logformat, datefmt='%b %d %H:%M:%S',level=logging.DEBUG)

# Download CVE
# url and path are specified in config.py
def downCve():
    url=app.config.get('CVE_URL')
    outfile=app.config.get('CVE_GZ')
    req=urllib.request.Request(url)
    r=urllib.request.urlopen(req)
    log.info('GET %s', url, extra=logvar)
    gz_data=r.read()
    log.info('write cve list to %s', outfile, extra=logvar)
    with open(outfile, 'wb') as g:
        g.write(gz_data)
    return 1

# Read and parse CVE
# Return a dict
def readCve():
    cve={}
    log.info('opening %s', app.config.get('CVE_GZ'), extra=logvar)
    with gzip.open(app.config.get('CVE_GZ'), 'r') as f:
       # a=gzip.decompress(f)
        for line in f:
            line=str(line)
            # line filter (line content match cve_search)
            cve_search=re.search('^b\'(CVE[\d-]+),(.*?),(.*?)\|.*$', line)
            if cve_search:
                tmp_id=cve_search.group(1)
                tmp_status=cve_search.group(2)
                tmp_desc=cve_search.group(3)

                # Filter Cisco devices ( filter Cisco/IOS )
                cisco_search=re.search('Cisco| IOS ', tmp_desc )
                if cisco_search:
                    cve_id=tmp_id
                    cve[cve_id]={}
                    cve[cve_id]['version']='IOS 12.24'
                    cve[cve_id]['status']=tmp_status
                    cve[cve_id]['description']=tmp_desc
                else:
                # next if not cisco devices
                    continue

                tab=line.split('|')
                for j in tab:
                    # Search url
                    url_search=re.search('\w+:(http://.*?)[ ",]',j)
                    if url_search:
                        try:
                            cve[cve_id]['url']+='\n'+url_search.group(1)
                        except :
                            cve[cve_id]['url']=url_search.group(1)
    log.debug('End readCve()', extra=logvar)
    return cve

def updateCve(cve_dict):
    # sqlreq='SELECT COUNT(id) FROM vulncve;'
    sqlreq = db.session.query(db.func.count(VulnCve.id)).first()
    id_count=sqlreq[0]
    log.debug('Start updateCve', extra=logvar)
    if id_count > 0:
        log.info('Table vulncve is not empty', extra=logvar)
    else:
        log.info('Table vulncve is empty', extra=logvar)

    # Organize and add data to database
    db_fields=( 'description','status', 'url' )
    for cve_id in sorted(cve_dict):
        for f in db_fields:
            if not f in cve_dict[cve_id].keys():
                cve_dict[cve_id][f]=''

        obj=VulnCve()
        obj.cve_id=cve_id
        for entry in cve_dict[cve_id]:

            if entry == 'url':
                obj.url=cve_dict[cve_id][entry]

            elif entry == 'description':
                desc=re.sub(r"([\"'])", r"", cve_dict[cve_id][entry])
                obj.description=re.sub(r"([%;])", r"\\\1", desc)

            elif entry == 'status':
                obj.status=cve_dict[cve_id][entry]


            elif entry == 'version':
                obj.version=cve_dict[cve_id][entry]
            db.session.add(obj)
            db.session.commit()

        log.info('Add CVE: '+cve_id, extra=logvar)
