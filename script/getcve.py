#! /usr/bin/python3.4

# FIXME : pb insert && select count(id)
# FIXME : get OS version + add version to sqlreq
# FIXME : use VulnCve table 


import gzip
import logging
import os
import re
from sqlalchemy import Table, MetaData, create_engine, select, cast
import tempfile
import urllib.request

# File path
cve_url='http://cve.mitre.org/data/downloads/allitems.csv.gz'
cve_csv='cve.csv.gz'
logfile='log/lostinnetwork.log'

## Log configuration
uid=os.getlogin()
d= { 'user' :  uid }
# Print log with same format as default syslog
logformat='%(asctime)s %(user)s %(name)s[%(process)d] %(levelname)s %(message)s' 
log=logging.getLogger('LOSTINNETWORK')
logging.basicConfig(filename='log/lostinnetwork.log',format=logformat, datefmt='%b %d %H:%M:%S',level=logging.DEBUG)


# Remove delete=False in production
tmpfile=tempfile.NamedTemporaryFile(delete=False)
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
    

# conect to db
engine = create_engine('postgresql://lin:lin@localhost/lin')
with engine.connect() as conn:

# Find last index of cve table
    sqlreq='SELECT COUNT(id) FROM vulncve;'
    result=conn.execute(sqlreq)
    res=result.fetchone()
    id_count=res['count']                    
    cve_count=0
    
    if id_count > 0:
        cve_count=id_count
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
                
        for entry in cve[cve_id]:
            if entry == 'url':
                url=cve[cve_id][entry]
            elif entry == 'description':
                desc=re.sub(r"([\"'])", r"", cve[cve_id][entry])
                desc=re.sub(r"([%;])", r"\\\1", desc) 
            elif entry == 'status':
                status=cve[cve_id][entry]
#            elif entry == 'version':
#                version=cve[cve_id][entry]
    
        # 
        if id_count > 0:
            sqlreq="SELECT count(id) FROM vulncve WHERE cve_id='"+cve_id+"';"
            result=conn.execute(sqlreq)
            res=result.fetchone()
            i=res['count']
            if i > 0:
                continue
    
        sqlreq="INSERT INTO vulncve VALUES("+str(cve_count)+",'"+cve_id+"','"+version+"','"+desc+"','"+url+"','"+status+"')"
        try:
            result=conn.execute(sqlreq)
            log.debug('ADD: %s', cve_id, extra=d)
            cve_count+=1
        except:
            log.debug('FAIL add: %s', cve_id, extra=d)

