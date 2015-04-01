#!/usr/bin/python3
# coding=utf-8
# Version 1.0
# Author hiziv

try:
    import Queue
except ImportError:
    import queue as Queue
import threading
import time
from app.models.device import Device
from app.utils.crypto import PasswordManager
from app import app
import pexpect
import re

PROMPT_REGEX_DEBIAN = "\r\n[^\r\n ]+:[^\r\n]+[\\\$#][ ]*"  # 20121312-YRG:
PROMPT_REGEX_IPSO = "\r\n[^\r\n ]+\\\[[^\r\n]+\\\]#[ ]*"  # 20121312-YRG:
PROMPT_REGEX_SPLAT = "\r\n\\\[[^\r\n ]+@[^\r\n]+\\\]#[ ]*"  # 20121312-YRG
PROMPT_REGEX_REDHAT = "\r\n\\\[[^\r\n ]+@[^\r\n]+\\\][\\\$#][ ]*"  # 20121
PROMPT_REGEX_JUNOS = "\r\n[^\r\n ]+@[^\r\n]+[\\\]>[ ]*"
PROMPT_REGEX_JUNOSEDIT = "\r\n[^\r\n ]+@[^\r\n]+[\\\]#[ ]*"
# PROMPT_REGEX_GENTOO = "[^\n]+@[^\n]+ [^\n]+ \\\$|[^\n]+ [^\n]+ #";
# PROMPT_REGEX_POSIX = PROMPT_REGEX_DEBIAN.'|'.PROMPT_REGEX_IPSO.'|'.PROMPT_REGEX_SPLAT.'|'.PROMPT_REGEX_REDHAT;
PROMPT_REGEX_BLUECOAT = "\r\n[^\r\n ]+>[ ]*"  # 20121312-YRG: need to veri
PROMPT_REGEX_BLUECOATENABLE = "\r\n[^\r\n ]+#[ ]*"  # 20121312-YRG: need t
PROMPT_REGEX_BLUECOATCONFIG = "\r\n[^\r\n ]+#([^)]+)[ ]*"  # 20121312-YRG:
PROMPT_REGEX1_CISCO = "\r\n[\r]*[^\r\n\*># ]+[>#:][ ]*";
PROMPT_REGEX_CISCO = ".*[>#:][ ]*"  # 20152701-ALD
PROMPT_REGEX_CISCOASA = "\r\n\r[^\r\n\*># ]+[>#] "
PROMPT_REGEX_CISCOENABLE = "\r\n[\r]*[^\r\n\*# ]+#[ ]*"
PROMPT_REGEX_NETSCREEN = "\r\n[^\r\n ]+([^\r\n ]+)->[ ]*"  # 20121312-YRG
# PROMPT_REGEX_TIPPINGPOINT = "\r\n[^\r\n ]+#";
PROMPT_REGEX_TIPPINGPOINT = "[\r\n]+[^\r\n ]+#[ ]*"  # TippingPoint is
PROMPT_REGEX_IRONPORT = "\r\n[\r]*[^\r\n\*># ]+>[ ]*"
PROMPT_REGEX_NETSCALER = "\r\n[\r]*>[ ]*"

# Definition command to send depend to the devicetype
Regex = {
    'Cisco': (PROMPT_REGEX_CISCO, PROMPT_REGEX_CISCOENABLE),
    'ciscoASA': (PROMPT_REGEX_CISCOASA, PROMPT_REGEX_CISCOENABLE)
}
ComCiscoISR = {'sh ip route': 'route', 'sh run': 'run', 'sh version' : 'version'}

directory = 'data/'

def mainsendcommand():
    # derror={}
    exit_flag = 0

    class myThread(threading.Thread):
        def __init__(self, threadID, name, q):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.q = q

        def run(self):
            print("Starting " + self.name)
            process_data(self.name, self.q)
            print("Exiting " + self.name)

    def process_data(threadName, q):
        while not exit_flag:
            queueLock.acquire()
            if not workQueue.empty():
                data = q.get()
                queueLock.release()
                print( send(data))
            else:
                queueLock.release()
            time.sleep(1)

    threadList = ["Thread-1", "Thread-2", "Thread-3"]
    queueLock = threading.Lock()
    workQueue = Queue.Queue(2000)
    threads = []
    threadID = 1
    nameList = []

    for device in Device.query.all():
        password = PasswordManager.decrypt_string(device.password, PasswordManager.generate_pwdh_from_password("root"))
        username = device.username
        method = 'ssh'
        enable = PasswordManager.decrypt_string(device.enapassword, PasswordManager.generate_pwdh_from_password("root"))
        print(device.name + ' ' + device.ip + ' ' + username + ' ' + password + ' ' + enable + ' ' + device.devicetype.name)
        nameList.append(method + "," + device.name + "," + device.ip + "," + username + "," + password + "," + enable + "," + device.devicetype.manufacturer.name)


        # Create new threads
    for tName in threadList:
        thread = myThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1

    # Fill the queue
    queueLock.acquire()
    for word in nameList:
        print(word)
        workQueue.put(word)
    queueLock.release()

    # Wait for queue to empty
    while not workQueue.empty():
        pass

    # Notify threads it's time to exit
    exit_flag = 1

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print("Exiting Main Thread")





def send(data):
    derror = {}
    x = data.split(",")
    sMethod = (x[0])
    sHostname = (x[1])
    sIp = (x[2])
    sUsername = (x[3])
    sPassword = (x[4])
    sEnable = (x[5])
    sDeviceType = (x[6])
    print (data)
    if sMethod == "scp":
        app.logger.info('connecting to ' + sUsername + '@' + sIp + ' ' + sHostname + ' whith ' + sMethod)
        for key in ComUnix:
            child = pexpect.spawn('scp %s@%s:%s %s/%s-%s.txt' % (sUsername, sIp, key, directory, sHostname, ComUnix[key]))
            #q = child.expect(['assword:',r"yes/no",pexpect.TIMEOUT,pexpect.EOF], timeout=30)
            q = child.expect(['assword:',PROMPT_ADD_KNOWN_HOST,pexpect.TIMEOUT,pexpect.EOF], timeout=30)
            if q == 0:
                child.sendline(sPassword)
            elif q == 1:
                child.sendline("yes")
                child.expect("assword:", timeout=30)
                child.sendline(password)
            elif q == 2:
                derror[sHostname]='TIMEOUT'
                return derror
            elif q == 3:
                derror[sHostname]='EOF'
                return derror
            else:
                derror[sHostname]='unknown error'
                return derror
            data = child.read()
            derror[sHostname]='all is fine ;)'
            child.close()
    elif (sMethod == "ssh" or sMethod == "telnet"):
        if sMethod == "ssh":
            sTunnel = ('ssh -o ConnectTimeout=25 -o StrictHostKeyChecking=no -l ' + sDeviceType + ' ')
            app.logger.info('connecting to ' + sUsername + '@' + sIp + ' ' + sHostname + ' whith ' + sMethod + ' and tunnel is ' + sTunnel)
            child = pexpect.spawn(sTunnel + sUsername + '@' + sIp)
        elif sMethod == "telnet":
            sTunnel = 'telnet '
            app.logger.info('connecting to ' + sIp + ' ' + sHostname + ' whith ' + sMethod + ' and tunnel is ' + sTunnel)
            child = pexpect.spawn(sTunnel + sIp)
            m = child.expect([PROMPT_REGEX_CISCO, pexpect.TIMEOUT, pexpect.EOF])
            if m == 0:
                child.sendline(sUsername)
            elif m == 1:
                derror[sHostname] = 'TIMEOUT'
                return derror
            elif m == 2:
                derror[sHostname] = 'EOF'
                return derror
        m = child.expect([PROMPT_REGEX_CISCO, 'assword:', pexpect.TIMEOUT, pexpect.EOF])
        if m == 0:
            child.sendline(sPassword)
        elif m == 1:
            child.sendline(sPassword)
        elif m == 2:
            derror[sHostname] = 'TIMEOUT'
            return derror
        elif m == 3:
            print ('maybe here')
            derror[sHostname] = 'EOF'
            return derror
        else:
            child.sendline(sPassword)
        q = child.expect(['>', '[Pp]assword:', pexpect.TIMEOUT, pexpect.EOF])
        #q = child.expect([PROMPT_REGEX_CISCO, pexpect.TIMEOUT, pexpect.EOF])
        if q == 0:
            print ('send enable 11')
            child.sendline('enable')
        elif q == 1:
            derror[sHostname] = 'wrong password'
        elif q == 2:
            print ('maybe here TIMEOUT')
            derror[sHostname] = 'TIMEOUT'
            return derror
        elif q == 3:
            derror[sHostname] = 'EOF'
            return derror
        else:
            print ('send enable 2')
            child.sendline('enable')
        q = child.expect(['assword:', '>', pexpect.TIMEOUT, pexpect.EOF])
        if q == 0:
            child.sendline(sEnable)
        elif q == 1:
            child.sendline(sEnable)
        elif q == 2:
            print ('maybe here TIMEOUT 2')
            derror[sHostname] = 'TIMEOUT'
            return derror
        elif q == 3:
            derror[sHostname] = 'EOF'
        if sDeviceType == "Cisco":
            q = child.expect([PROMPT_REGEX_CISCOENABLE, '>', pexpect.TIMEOUT, pexpect.EOF])
            if q == 0:
                child.sendline('terminal length 0')
            elif q == 1:
                derror[sHostname] = 'wrong enable password'
                return derror
            elif q == 2:
                derror[sHostname] = 'TIMEOUT'
                return derror
            elif q == 3:
                derror[sHostname] = 'EOF'
                return derror
            q = child.expect([PROMPT_REGEX_CISCOENABLE, pexpect.TIMEOUT, pexpect.EOF])
            for key in ComCiscoISR:
                if q == 0:
                    child.sendline(key)
                elif q == 1:
                    derror[sHostname] = 'TIMEOUT'
                    return derror
                elif q == 2:
                    derror[sHostname] = 'EOF'
                    return derror
                q = child.expect([PROMPT_REGEX_CISCOENABLE, pexpect.TIMEOUT, pexpect.EOF])
                with open(directory + sHostname + '-' + ComCiscoISR[key] + '.txt', 'wb') as fd:
                    fd.write(child.before)
            child.sendline('exit')
            return derror
        else:
            print('not cisco')
    else:
        derror[sHostname] = sMethod + ' not supported'



if __name__ == '__mainsendcommand__':
    mainsendcommand()

