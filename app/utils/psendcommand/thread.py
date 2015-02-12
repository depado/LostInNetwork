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

from app.utils.psendcommand.psendcommand import send
from app.models.device import Device
from app.utils.crypto import PasswordManager


def mainthread():
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
                # print ("%s processing %s" % (threadName, data))
                print(data)
                print(send(data))
            else:
                queueLock.release()
            time.sleep(1)

    threadList = ["Thread-1", "Thread-2", "Thread-3"]
    # nameList = ["One", "Two", "Three", "Four", "Five"]
    queueLock = threading.Lock()
    workQueue = Queue.Queue(2000)
    threads = []
    threadID = 1
    nameList = []

    # list_devices=open('list.txt').readlines() #This will read the list of devices that file is on the same location as the script -- it's something I have to change

    # pdb.set_trace()
    #for i in list_devices:
    #    x=i.split ()
    #    if len(x) == 7 :
    #        sMethod = (x[0])
    #        sHostname = (x[1])
    #        sIp = (x[2])
    #        sUsername = (x[3])
    #        sPassword = (x[4])
    #        sEnable = (x[5])
    #        sUID = (x[6])
    #        nameList.append(sMethod + "," + sHostname + "," + sIp + "," + sUsername + "," + sPassword + "," + sEnable + "," + sUID)    
    #    else:
    #        print ('not enough arguments for device ' + x[1])

    for device in Device.query.all():
        password = PasswordManager.decrypt_string(device.password, PasswordManager.generate_pwdh_from_password("root"))
        username = 'admin'
        method = 'ssh'
        enable = 'enablepass'
        # enapassword = PasswordManager.decrypt_string(device.enapassword,PasswordManager.generate_pwdh_from_password("root"))
        print(device.name + ' ' + device.ip + ' ' + username + ' ' + password + ' ' + device.devicetype.name)
        #print(device.method + ' '+ device.name + ' ' + device.ip + ' ' + device.username + ' ' + passwrd + ' ' + enapassword + ' ' + device.devicetype.name)
        #Device[0].decrypt_password(
        nameList.append(
            method + "," + device.name + "," + device.ip + "," + username + "," + password + "," + enable + "," + device.devicetype.manufacturer.name)




        # Create new threads
    for tName in threadList:
        thread = myThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1

    # Fill the queue
    queueLock.acquire()
    for word in nameList:
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


if __name__ == '__mainthread__':
    mainthread()

