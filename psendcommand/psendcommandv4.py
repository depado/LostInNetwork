#!/usr/bin/python3
# Version 1.0
# Author hiziv
import pdb
import os,sys,string
#sys.path.append('/home/user/python/lib/lib/python')
import pexpect

#adict={}

#def send(Method,Hostname,Ip,Username,Password,Enable,UID):
def send(data):
	x=data.split (",")
	sMethod = (x[0])
	sHostname = (x[1])
	sIp = (x[2])
	sUsername = (x[3])
	sPassword = (x[4])
	sEnable = (x[5])
	sUID = (x[6])

	if sMethod == "ssh":
		#sTunnel = ('ssh -o StrictHostKeyChecking=no -l ' + sUID + ' ')
		sTunnel = ('ssh -o ConnectTimeout=25 -o StrictHostKeyChecking=no -l ' + sUID + ' ')
		print ('connecting to ' + sUsername + '@' + sIp + ' ' + sHostname + ' whith ' + sMethod + ' and tunnel is ' + sTunnel)
		child = pexpect.spawn(sTunnel + sUsername + '@' + sIp)
	elif sMethod == "telnet":
		sTunnel = 'telnet '
		print ('connecting to ' + sIp + ' ' + sHostname + ' whith ' + sMethod + ' and tunnel is ' + sTunnel)
		child = pexpect.spawn(sTunnel + sIp)
		m = child.expect (['assword:','[Ll]ogin:','[Uu]sername',pexpect.TIMEOUT,pexpect.EOF])
		if m==0:
			child.sendline(sPassword)
			print ('child.sendline sPassword')
		elif m==1:
			child.sendline(sUsername)
			print ('child.sendline sUsername')
		elif m==2:
			child.sendline(sUsername)
			print ('child.sendline sUsername')
		elif m==3:
			#adict={sHostname:'TIMEOUT'}
			print ("login error")
			return
		elif m==4:
			print ("111 no login prompt error")
			return
	m = child.expect (['assword:','[Ll]ogin:','[Uu]sername',pexpect.TIMEOUT,pexpect.EOF])
	if m==0:
		child.sendline(sPassword)
		print ('child.sendline sPassword')
	elif m==1:
		child.sendline(sUsername)
		print ('child.sendline sUsername')
	elif m==2:
		child.sendline(sUsername)
		print ('child.sendline sUsername')
	elif m==3:
		#adict={sHostname:'TIMEOUT'}
		print ("TIMEOUT")
		return
	elif m==4:
		print ("222 no login prompt error")
		print (child.before)
		return
	q = child.expect (['>','[Pp]assword:',pexpect.TIMEOUT,pexpect.EOF])
	if q==0:
		child.sendline ('ena')
	elif q==1:
		#adict[sHostname] = 'wrong password'
		print ('wrong password')
		#return adict 
	elif q==2:
		print ('wait too long for prompt')
		return
	elif q==3:
		return
	q = child.expect (['assword:','>',pexpect.TIMEOUT,pexpect.EOF])
	if q==0:
		child.sendline (sEnable)
	elif q==1:
		child.sendline (sEnable)
	elif q==2:
		print ('return 2')
		return
	elif q==3:
		print ('return 3')
	q = child.expect (['#','>',pexpect.TIMEOUT,pexpect.EOF])
	if q==0:
		child.sendline ('terminal length 0')
	elif q==1:
		return
	elif q==2:
		return
	q = child.expect (['#',pexpect.TIMEOUT,pexpect.EOF])
	if q==0:
		child.sendline ('sh run')
	elif q==1:
		print ('return 2')
		return
	elif q==2:
		print ('return 3')
		return
	q = child.expect (['#',pexpect.TIMEOUT,pexpect.EOF])
	result=open(sHostname + '.txt','wb')
	result.write(child.before)
	result.close
	#return adict

#list_devices=open('list.txt').readlines() #This will read the list of devices that file is on the same location as the script -- it's something I have to change

##pdb.set_trace()
#for i in list_devices:
#	x=i.split ()
#	if len(x) == 7 :
#		sMethod = (x[0])
#		sHostname = (x[1])
#		sIp = (x[2])
#		sUsername = (x[3])
#		sPassword = (x[4])
#		sEnable = (x[5])
#		sUID = (x[6])
#		send(sMethod,sHostname,sIp,sUsername,sPassword,sEnable,sUID)	
#		#print (adict)
#	else:
#		print ('not enough arguments for device ' + x[1])
#



print ('psendcommand done')
