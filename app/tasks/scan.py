# -*- coding: utf-8 -*-

import celery
import pexpect
import redis

from celery import group

from app import app
from app.models import Device
from app.utils.prompt_regex import *
from app.utils.crypto import PasswordManager


SCAN_KEY = "scan_task_uuid"
SCAN_LOCK = redis.Redis().lock("celery_scan_lock")


@celery.task(bind=True)
def scan_all_devices_async(self, pwdh):
    have_lock = False
    try:
        have_lock = SCAN_LOCK.acquire(blocking=False)
        app.logger.info(msg="Started")
        jobs = list()
        for device in Device.query.all():
            jobs.append(scan_device_async.subtask((device, device.devicetype, device.devicetype.manufacturer, pwdh)))
        job = group(jobs)
        result = job.apply_async()
        app.logger.info("Waiting for results")
        result.join()
        app.logger.info(msg="{}".format(result))
        app.logger.info(msg="Got all results")
    finally:
        if have_lock:
            SCAN_LOCK.release()


@celery.task(bind=True)
def scan_device_async(self, device, devicetype, manufacturer, pwdh):
    """
    Calls the scan_device function async way.
    """
    scan_device(device, devicetype, manufacturer, pwdh, async=self)


def scan_device(device, devicetype, manufacturer, pwdh, async=None):
    password = PasswordManager.decrypt_string(device.password, pwdh)
    enapassword = PasswordManager.decrypt_string(device.enapassword, pwdh)
    derror = {}
    if device.method in ['ssh', 'telnet']:
        if device.method == "ssh":
            sTunnel = ('ssh -o ConnectTimeout=25 -o StrictHostKeyChecking=no -l ' + manufacturer.name + ' ')
            app.logger.info('Connecting to ' + device.username + '@' + device.ip + ' ' + device.name + ' whith ' + device.method + ' and tunnel is ' + sTunnel)
            child = pexpect.spawn(sTunnel + device.username + '@' + device.ip)
        else:
            sTunnel = 'telnet '
            app.logger.info('connecting to ' + device.ip + ' ' + device.name + ' whith ' + device.method + ' and tunnel is ' + sTunnel)
            child = pexpect.spawn(sTunnel + device.ip)
            m = child.expect([PROMPT_REGEX_CISCO, pexpect.TIMEOUT, pexpect.EOF])
            if m == 0:
                child.sendline(device.username)
            elif m == 1:
                derror[device.name] = 'TIMEOUT'
                return derror
            elif m == 2:
                derror[device.name] = 'EOF'
                return derror
        m = child.expect([PROMPT_REGEX_CISCO, 'assword:', pexpect.TIMEOUT, pexpect.EOF])
        if m in [0, 1]:
            child.sendline(password)
        elif m == 2:
            derror[device.name] = 'TIMEOUT'
            return derror
        elif m == 3:
            derror[device.name] = 'EOF'
            return derror
        else:
            child.sendline(password)
        q = child.expect(['>', '[Pp]assword:', pexpect.TIMEOUT, pexpect.EOF])
        # q = child.expect([PROMPT_REGEX_CISCO, pexpect.TIMEOUT, pexpect.EOF])
        if q == 0:
            child.sendline('enable')
        elif q == 1:
            derror[device.name] = 'wrong password'
        elif q == 2:
            derror[device.name] = 'TIMEOUT'
            return derror
        elif q == 3:
            derror[device.name] = 'EOF'
            return derror
        else:
            child.sendline('enable')
        q = child.expect(['assword:', '>', pexpect.TIMEOUT, pexpect.EOF])
        if q == 0:
            child.sendline(enapassword)
        elif q == 1:
            child.sendline(enapassword)
        elif q == 2:
            derror[device.name] = 'TIMEOUT'
            return derror
        elif q == 3:
            derror[device.name] = 'EOF'
        if manufacturer.name == "Cisco":
            q = child.expect([PROMPT_REGEX_CISCOENABLE, '>', pexpect.TIMEOUT, pexpect.EOF])
            if q == 0:
                child.sendline('terminal length 0')
            elif q == 1:
                derror[device.name] = 'wrong enable password'
                return derror
            elif q == 2:
                derror[device.name] = 'TIMEOUT'
                return derror
            elif q == 3:
                derror[device.name] = 'EOF'
                return derror
            q = child.expect([PROMPT_REGEX_CISCOENABLE, pexpect.TIMEOUT, pexpect.EOF])
            for key in ComCiscoISR:
                if q == 0:
                    child.sendline(key)
                elif q == 1:
                    derror[device.name] = 'TIMEOUT'
                    return derror
                elif q == 2:
                    derror[device.name] = 'EOF'
                    return derror
                q = child.expect([PROMPT_REGEX_CISCOENABLE, pexpect.TIMEOUT, pexpect.EOF])
                with open(app.config.get('CONF_DIR') + device.name + '-' + ComCiscoISR[key] + '.txt', 'wb') as fd:
                    fd.write(child.before)
            child.sendline('exit')
            return derror
        else:
            print('not cisco')
    else:
        derror[device.name] = device.method + ' not supported'
