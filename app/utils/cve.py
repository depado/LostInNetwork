# -*- coding: utf-8 -*-

import gzip
import logging
import os
import re
import urllib.request

from app import app
from app import db
from app.models import VulnCve

uid = os.getlogin()
logvar = {'user': uid}
logformat = '%(asctime)s %(user)s %(name)s[%(process)d] %(levelname)s %(message)s'
log = logging.getLogger('LOSTINNETWORK')
logging.basicConfig(
    filename=app.config.get('LOG_FILE'),
    format=logformat,
    datefmt='%b %d %H:%M:%S',
    level=logging.DEBUG
)

def down_cve():
    """
    Download CVE
    url and path are specified in config.py
    """
    try:
        url=app.config.get('CVE_URL')
        outfile=app.config.get('CVE_GZ')
        req=urllib.request.Request(url)
        r=urllib.request.urlopen(req)
        log.info('GET %s', url, extra=logvar)
        gz_data=r.read()
        log.info('write cve list to %s', outfile, extra=logvar)
        with open(outfile, 'wb') as g:
            g.write(gz_data)
        return True
    except Exception as e:
        print(e)
        return False

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
                        except Exception as e:
                            log.info(e, extra=logvar)
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
        if id_count != 0:
            sqlreq = db.session.query(VulnCve).filter( VulnCve.cve_id == cve_id ).first()
            if sqlreq:
                log.info(cve_id+' already exist in db', extra=logvar)
                continue


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
    log.info('Update Finished', extra=logvar)
