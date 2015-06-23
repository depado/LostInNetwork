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
import pexpect

from app import app
from app.models.device import Device
from app.utils.crypto import PasswordManager
from app.utils.prompt_regex import *

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
    if (sMethod == "ssh" or sMethod == "telnet"):
        if sMethod == "ssh":
            sTunnel = ('ssh -o ConnectTimeout=25 ')
            app.logger.info('connecting to ' + sUsername + '@' + sIp + ' ' + sHostname + ' with ' + sMethod + ' and tunnel is ' + sTunnel)
            child = pexpect.spawn(sTunnel + sUsername + '@' + sIp)
        elif sMethod == "telnet":
            sTunnel = 'telnet '
            app.logger.info('connecting to ' + sIp + ' ' + sHostname + ' with ' + sMethod + ' and tunnel is ' + sTunnel)
            child = pexpect.spawn(sTunnel + sIp)
            q = child.expect([PROMPT_REGEX_CISCO,pexpect.TIMEOUT, pexpect.EOF])
            if q == 0:
                child.sendline(sUsername)
            elif q == 1:
                derror[sHostname] = 'TIMEOUT'
                return derror
            elif m == 2:
                derror[sHostname] = 'EOF'
                return derror
        q = child.expect(['.* continue connecting (yes/no)?',PROMPT_REGEX_CISCO, pexpect.TIMEOUT, pexpect.EOF])
        if q == 0:
            child.sendline('yes')
            q = child.expect(['assword:', pexpect.TIMEOUT, pexpect.EOF])
            if q == 0:
                child.sendline(sPassword)
            elif q == 1:
                derror[sHostname] = 'TIMEOUT'
                return derror
            elif q == 2:
                derror[sHostname] = 'EOF'
                return derror
        elif q == 1:
            child.sendline(sPassword)
        elif q == 3:
            derror[sHostname] = 'TIMEOUT'
            return derror
        elif q == 4:
            derror[sHostname] = 'EOF'
            return derror
        else:
            child.sendline(sPassword)

        #connection is ok, can right now send commands to the device
        q = child.expect([PROMPT_REGEX_CISCO, pexpect.TIMEOUT, pexpect.EOF])
        if q == 0:
            child.sendline('enable')
        elif q == 1:
            derror[sHostname] = 'wrong password'
        elif q == 2:
            derror[sHostname] = 'TIMEOUT 1'
            return derror
        elif q == 3:
            derror[sHostname] = 'EOF'
            return derror
        else:
            child.sendline('enable')
        q = child.expect([PROMPT_REGEX_CISCO, pexpect.TIMEOUT, pexpect.EOF])
        if q == 0:
            child.sendline(sEnable)
        elif q == 1:
            child.sendline(sEnable)
        elif q == 2:
            derror[sHostname] = 'TIMEOUT'
            return derror
        elif q == 3:
            derror[sHostname] = 'EOF'
        if sDeviceType == "Cisco":
            #q = child.expect([PROMPT_REGEX_CISCOENABLE, '>', pexpect.TIMEOUT, pexpect.EOF])
            q = child.expect([PROMPT_REGEX_CISCO, '>', pexpect.TIMEOUT, pexpect.EOF])
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
            derror[sHostname] = 'ALL FINE'
            return derror
        else:
            print('not cisco')
    
    elif sMethod == 'scp':
        print ('I will do smoething ;)')
    else:
        derror[sHostname] = sMethod + ' not supported'


if __name__ == '__mainsendcommand__':
    mainsendcommand()

