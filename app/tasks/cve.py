# -*- coding: utf-8 -*-

import gzip
import re
import urllib.request
import redis
import celery
import time

from app import app
from app import db
from app.models.vuln import VulnCve

CVE_KEY = "cve_task_uuid"
CVE_LOCK = redis.Redis().lock("celery_cve_lock")

VERSION_PATTERN='^b\'(CVE[\d-]+),.*IOS (\d+\.\d+\.?\d*).*?(through|and)? (\d+\.\d+\.?\d*)?.*$'


def get_version(currentline):
    """
    get_version from cve
    """
    line=str(currentline)
    version2 = []
    separator = ''
    version = ''
    multi_version_search=re.search(VERSION_PATTERN, line)
    if multi_version_search:
        version2.append(multi_version_search.group(2))
        separator = multi_version_search.group(3)
        if multi_version_search.group(4):
            version2.append(multi_version_search.group(4))

    if separator == 'through':
        version = '-'.join(version2)
    elif separator == 'and':
        version = ','.join(version2)
    else:
        for vers in version2:
            if vers:
                version = str(vers)
    return str(version)


@celery.task(bind=True)
def cve_async(self):
    have_lock = False
    try:
        have_lock = CVE_LOCK.acquire(blocking=False)
        self.update_state(state='PROGRESS', meta={'message': "Downloading CVE", 'percentage': 5})
        try:
            url = app.config.get('CVE_URL')
            outfile = app.config.get('CVE_GZ')
            req = urllib.request.Request(url)
            r = urllib.request.urlopen(req)
            gz_data = r.read()
            with open(outfile, 'wb') as g:
                g.write(gz_data)
        except Exception as e:
            app.logger.error(e)
            return False

        self.update_state(state='PROGRESS', meta={'message': "Reading Downloaded CVE", 'percentage': 15})
        cve={}
        with gzip.open(app.config.get('CVE_GZ'), 'r') as f:
            for line in f:
                line=str(line)
                cve_search=re.search('^b\'(CVE[\d-]+),(.*?),(.*?)\|.*$', line)
                if cve_search:
                    tmp_id=cve_search.group(1)
                    tmp_status=cve_search.group(2)
                    tmp_desc=cve_search.group(3)

                    # Filter Cisco devices ( filter Cisco/IOS )
                    cisco_search=re.search('Cisco| IOS ', tmp_desc)
                    if cisco_search:
                        cve_id=tmp_id
                        cve[cve_id]={}
                        cve[cve_id]['version']=get_version(line)
                        cve[cve_id]['status']=tmp_status
                        cve[cve_id]['description']=tmp_desc
                    else:
                        # next if not cisco devices
                        continue

                    tab=line.split('|')
                    for j in tab:
                        # Search url
                        url_search=re.search('\w+:(http://.*?)[ ",]', j)
                        if url_search:
                            try:
                                cve[cve_id]['url'] += '\n' + url_search.group(1)
                            except Exception as e:
                                app.logger.info(e)
                                cve[cve_id]['url']=url_search.group(1)
        cve_dict = cve
        sqlreq = db.session.query(db.func.count(VulnCve.id)).first()
        id_count=sqlreq[0]
        self.update_state(state='PROGRESS', meta={'message': "Start Updating CVE", 'percentage': 20})
        db_fields=('description', 'status', 'url')
        total = len(cve_dict)
        for current, cve_id in enumerate(sorted(cve_dict)):
            if id_count != 0:
                sqlreq = db.session.query(VulnCve).filter(VulnCve.cve_id == cve_id).first()
                if sqlreq:
                    self.update_state(state='PROGRESS', meta={
                        'message': "Adding CVE {cve_id} ({current}/{total})".format(cve_id=cve_id, current=current,
                                                                                    total=total),
                        'percentage': current / total * 100 + 20 - (current / total * 20)
                    })
                    continue

            for f in db_fields:
                if f not in cve_dict[cve_id].keys():
                    cve_dict[cve_id][f] = ''
            obj = VulnCve()
            obj.cve_id=cve_id
            for entry in cve_dict[cve_id]:
                if entry == 'url':
                    obj.url = cve_dict[cve_id][entry]
                elif entry == 'description':
                    desc=re.sub(r"([\"'])", r"", cve_dict[cve_id][entry])
                    obj.description=re.sub(r"([%;])", r"\\\1", desc)
                elif entry == 'status':
                    obj.status=cve_dict[cve_id][entry]
                elif entry == 'version':
                    obj.version=cve_dict[cve_id][entry]
            db.session.add(obj)
            self.update_state(state='PROGRESS', meta={
                'message': "Adding CVE {cve_id} ({current}/{total})".format(cve_id=cve_id, current=current,
                                                                            total=total),
                'percentage': current / total * 100 + 20 - (current / total * 20)
            })
        self.update_state(state='PROGRESS', meta={'message': "Update Finished", 'percentage': 100})
        time.sleep(5)
        db.session.commit()
    finally:
        if have_lock:
            CVE_LOCK.release()
