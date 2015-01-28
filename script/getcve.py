#! /usr/bin/python3.4

# FIXME : pb insert && select count(id)
# FIXME : get OS version + add version to sqlreq
# FIXME : use VulnCve table 


import urllib.request
import gzip
import re
from sqlalchemy import Table, MetaData, create_engine, select, cast

# path
cve_url='http://cve.mitre.org/data/downloads/allitems.csv.gz'
cve_csv='cve.csv'

cve={}
version='version'

# Download cve list
def getCve( url, outfile ):
	req=urllib.request.Request(url)
	r=urllib.request.urlopen(req)
	print('open url: ',url)
	gz_data=r.read()
	print('decompress data')
	data=gzip.decompress(gz_data)
	print('write data to',outfile)
	with open(outfile, 'wb') as f: 
		f.write(data)

# 
#getCve( cve_url, cve_csv )


print('opening',cve_csv)
with open(cve_csv, 'r', encoding='iso-8859-2') as fi:
	for line in fi:
		# line filter (line content match cve_search)	
		cve_search=re.search('^(CVE[\d-]+),(.*?),(.*?)\|.*$', line)
		if cve_search: 
			tmp_id=cve_search.group(1)
#			print('DEBUG no cisco: '+tmp_id)
			tmp_status=cve_search.group(2)
			tmp_desc=cve_search.group(3)
			# Filter Cisco devices ( filter Cisco/IOS )
			cisco_search=re.search('Cisco| IOS ', tmp_desc )
			if cisco_search:
				cve_id=tmp_id
#				print('DEBUG  cisco: '+tmp_id)
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
#						print('DEBUG',url_search.group(1), 'exist')
					except :
						cve[cve_id]['url']=url_search.group(1)
#						print('DEBUG',url_search.group(1), 'not exist')
	

# conect to db
engine = create_engine('postgresql://lin:lin@localhost/lin')
with engine.connect() as conn:

# Find last index of cve table
	sqlreq='SELECT COUNT(id) FROM cve;'
	result=conn.execute(sqlreq)
	res=result.fetchone()
	id_count=res['count']					
	cve_count=0
	
	if id_count > 0:
		cve_count=id_count
		print("DEBUG: Table cve is not empty")
	# DEBUG
	else:
		print("DEBUG: Table cve is empty")
	# END DEBUG
	
	# Organize and add data to database
	db_fields=( 'description','status', 'url' )
	for cve_id in sorted(cve):
		for f in db_fields:
			if not f in cve[cve_id].keys():
				cve[cve_id][f]=''
				
		for entry in cve[cve_id]:
	#		print(cve_id,entry,':',cve[cve_id][entry])
	#		print(entry)	
			if entry == 'url':
				url=cve[cve_id][entry]
			elif entry == 'description':
				desc=re.sub(r"([\"'])", r"", cve[cve_id][entry])
				desc=re.sub(r"([%;])", r"\\\1", desc) 
			elif entry == 'status':
				status=cve[cve_id][entry]
#			elif entry == 'version':
#				version=cve[cve_id][entry]
	
		# 
		if id_count > 0:
#			print("DEBUG: is "+cve_id+" is in table?")
			sqlreq="SELECT count(id) FROM cve WHERE cve_id='"+cve_id+"';"
			result=conn.execute(sqlreq)
			res=result.fetchone()
			i=res['count']
			if i > 0:
#				print("DEBUG: yes")
				continue
	
#		sqlreq="INSERT INTO cve VALUES("+str(cve_count)+",'"+cve_id+"','"+desc+"','"+url+"','"+status+"')"
		sqlreq="INSERT INTO vulncve VALUES("+str(cve_count)+",'"+cve_id+"','"+version+"','"+desc+"','"+url+"','"+status+"')"
		try:
			result=conn.execute(sqlreq)
			cve_count+=1
	#		print('DEBUG: '+cve_id)
		except:
#			print('DEBUG: '+cve_id+' ==>'+sqlreq)
			print('DEBUG FAIL: '+cve_id)

#engine = create_engine('postgresql://lin:lin@localhost/lin')
#with engine.connect() as conn:
#	result = conn.execute('select * from cve')
##	meta=MetaData()
#	print(result.fetchall())
