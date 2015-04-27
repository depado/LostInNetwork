# -*- coding: utf-8 -*-

import celery
import pexpect
import redis
import os
import time

from celery import group
from datetime import datetime

from app import app, db
from app.models import Device, Configuration
from app.utils.prompt_regex import *
from app.utils.crypto import PasswordManager


SCAN_KEY = "scan_task_uuid"
SCAN_LOCK = redis.Redis().lock("celery_scan_lock")

ERRORS = {
    0: 'TIMEOUT',
    1: 'EOF',
}


def generate_pexpect_list(expected):
    return [pexpect.TIMEOUT, pexpect.EOF] + expected


def perror(device, derror, val):
    if val in ERRORS:
        derror[device.name] = ERRORS[val]
        return True
    return False


def create_if_not_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_path(device, key):
    create_if_not_exist(os.path.join(app.config.get('CONF_DIR'), device.name))
    create_if_not_exist(os.path.join(app.config.get('CONF_DIR'), device.name, datetime.now().strftime("%Y%m%d")))
    return os.path.join(app.config.get('CONF_DIR'), device.name, datetime.now().strftime("%Y%m%d"), ComCiscoISR[key] +
                        "-" + datetime.now().strftime("%H:%M:%S") + '.txt')


@celery.task(bind=True)
def scan_all_devices_async(self, pwdh):
    have_lock = False
    try:
        have_lock = SCAN_LOCK.acquire(blocking=False)
        app.logger.info(msg="Started")
        jobs = list()
        for device in Device.query.all():
            jobs.append(scan_device_async.subtask((device, device.devicetype, device.devicetype.manufacturer, pwdh)))
        result = group(jobs).apply_async()
        while not result.ready():
            time.sleep(1)
            # TODO: Update status here
        app.logger.info(msg="Finished")
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
            s_tunnel = 'ssh -o ConnectTimeout=25 -o StrictHostKeyChecking=no '
            child = pexpect.spawn(s_tunnel + device.username + '@' + device.ip)
        else:
            s_tunnel = 'telnet '
            child = pexpect.spawn(s_tunnel + device.ip)
            m = child.expect(generate_pexpect_list([PROMPT_REGEX_CISCO]))
            if perror(device, derror, m):
                return derror
            if m == 2:
                child.sendline(device.username)
        q = child.expect(generate_pexpect_list([PROMPT_REGEX_CISCO, 'assword:']))
        if perror(device, derror, q):
            return derror
        if q in [2, 3]:
            child.sendline(password)
        else:
            child.sendline(password)
        q = child.expect(generate_pexpect_list(['>', '[Pp]assword:']))
        if perror(device, derror, q):
            return derror
        if q == 2:
            child.sendline('enable')
        elif q == 3:
            derror[device.name] = 'wrong password'
        else:
            child.sendline('enable')
        q = child.expect(generate_pexpect_list(['assword:', '>']))
        if perror(device, derror, q):
            return derror
        if q in [1, 2]:
            child.sendline(enapassword)
        if manufacturer.name == "Cisco":
            q = child.expect(generate_pexpect_list([PROMPT_REGEX_CISCOENABLE, '>']))
            if perror(device, derror, q):
                return derror
            if q == 2:
                child.sendline('terminal length 0')
            elif q == 3:
                derror[device.name] = 'wrong enable password'
                return derror
            q = child.expect(generate_pexpect_list([PROMPT_REGEX_CISCOENABLE]))
            for key in ComCiscoISR:
                if perror(device, derror, q):
                    return derror
                if q == 2:
                    child.sendline(key)
                q = child.expect(generate_pexpect_list([PROMPT_REGEX_CISCOENABLE]))
                path = get_path(device, key)
                with open(path, 'wb') as fd:
                    fd.write(child.before)
                PasswordManager.encrypt_file(path, pwdh)
                conf = Configuration()
                conf.path = path
                conf.device = device
                conf.date = datetime.now()
                db.session.add(conf)
                db.session.commit()
            child.sendline('exit')
            return derror
    else:
        derror[device.name] = device.method + ' not supported'
        return derror
