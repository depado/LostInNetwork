#!/usr/bin/python
# Version 1.0
# Author hiziv
import pdb
import os,sys,string
sys.path.append('/home/user/python/lib/lib/python')
import pexpect


list_devices=open('list.txt').readlines() #This will read the list of devices that file is on the same location as the script

#pdb.set_trace()
for i in list_devices:
	x=i.split ()
	if len(x) == 7 :
		sMethod = (x[0])
		sHostname = (x[1])
		sIp = (x[2])
		sUsername = (x[3])
		sPassword = (x[4])
		sEnable = (x[5])
		sUID = (x[6])
		if sMethod == "ssh":
			sTunnel = ('ssh -o StrictHostKeyChecking=no -l ' + sUID + ' ')
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
				print ("login error")
				continue
			elif m==4:
				print ("no login prompt error")
				continue
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
			print ("login error")
			continue
		elif m==4:
			print ("no login prompt error")
			continue
		q = child.expect (['>','[Pp]assword',pexpect.TIMEOUT,pexpect.EOF])
		if q==0:
			child.sendline ('ena')
		elif q==1:
			child.sendline (sPassword)
		elif q==2:
			print ("wrong password or wait too long for prompt")
			continue
		elif q==3:
			print ('continue 1')
			continue
		q = child.expect (['assword:','>',pexpect.TIMEOUT,pexpect.EOF])
		if q==0:
			child.sendline (sEnable)
		elif q==1:
			child.sendline (sEnable)
		elif q==2:
			print ('continue 2')
			continue
		elif q==3:
			print ('continue 3')
		q = child.expect (['#',pexpect.TIMEOUT,pexpect.EOF])
		if q==0:
			child.sendline ('terminal length 0')
		elif q==1:
			print ('continue 2')
			continue
		elif q==2:
			print ('continue 3')
			continue
		q = child.expect (['#',pexpect.TIMEOUT,pexpect.EOF])
		if q==0:
			child.sendline ('sh run')
		elif q==1:
			print ('continue 2')
			continue
		elif q==2:
			print ('continue 3')
			continue
		q = child.expect (['#',pexpect.TIMEOUT,pexpect.EOF])
		result=open(sHostname + '.txt','w')
		result.write(child.before + '\n')
		result.close
print ('psendcommand done')
