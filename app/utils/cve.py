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

def downCve():
    return 1

def updateCve():
    return 1
def upCve():
    # File path
    cve_url='http://cve.mitre.org/data/downloads/allitems.csv.gz'
    cve_csv='data/cve.csv.gz'
    logfile='log/lostinnetwork.log'

    ## Log configuration
    uid=os.getlogin()
    d= { 'user' :  uid }
    # Print log with same format as default syslog
    logformat='%(asctime)s %(user)s %(name)s[%(process)d] %(levelname)s %(message)s'
    log=logging.getLogger('LOSTINNETWORK')
    logging.basicConfig(filename=logfile,format=logformat, datefmt='%b %d %H:%M:%S',level=logging.DEBUG)


    # Remove delete=False in production
    tmpfile=tempfile.NamedTemporaryFile(delete=False,dir='tmp/')
    log.info('tmpfile name %s', tmpfile.name, extra=d)
    cve={}
    version='version'

    # Download cve list
    def getCve( url, outfile ):
        req=urllib.request.Request(url)
        r=urllib.request.urlopen(req)
        log.info('GET %s', url, extra=d)
        gz_data=r.read()
        log.info('decompress cve list', extra=d)
        data=gzip.decompress(gz_data)
        log.info('write cve list to %s', outfile, extra=d)
        with open(outfile, 'wb') as f:
            f.write(gz_data)
        with open(tmpfile.name, 'wb') as tf:
            tf.write(data)

    getCve( cve_url, cve_csv )

    log.info('opening %s', cve_csv, extra=d)
    with open(tmpfile.name, 'r', encoding='iso-8859-2') as fi:
        for line in fi:
            # line filter (line content match cve_search)
            cve_search=re.search('^(CVE[\d-]+),(.*?),(.*?)\|.*$', line)
            if cve_search:
                tmp_id=cve_search.group(1)
                tmp_status=cve_search.group(2)
                tmp_desc=cve_search.group(3)

                # Filter Cisco devices ( filter Cisco/IOS )
                cisco_search=re.search('Cisco| IOS ', tmp_desc )
                if cisco_search:
                    cve_id=tmp_id
                    cve[cve_id]={}
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



#        sqlreq='SELECT COUNT(id) FROM vulncve;'
        sqlreq = db.session.query(db.func.count(VulnCve.id)).first()
        id_count=sqlreq[0]

        if id_count > 0:
            log.info('Table vulncve is not empty', extra=d)
        # DEBUG
        else:
            log.info('Table vulncve is empty', extra=d)
        # END DEBUG

        # Organize and add data to database
        db_fields=( 'description','status', 'url' )
        for cve_id in sorted(cve):
            for f in db_fields:
                if not f in cve[cve_id].keys():
                    cve[cve_id][f]=''

            obj=VulnCve()
            obj.cve_id=cve_id
            for entry in cve[cve_id]:

                if entry == 'url':
                    obj.url=cve[cve_id][entry]

                elif entry == 'description':
                    desc=re.sub(r"([\"'])", r"", cve[cve_id][entry])
                    obj.description=re.sub(r"([%;])", r"\\\1", desc)

                elif entry == 'status':
                    obj.status=cve[cve_id][entry]


                elif entry == 'version':
                    obj.version='VersionNumber'
                    #obj.version=cve[cve_id][entry]
            db.session.add(obj)
            db.session.commit()
            log.info('Add CVE: '+cve_id, extra=d)
