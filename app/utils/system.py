# -*- coding: utf-8 -*-

from psutil import cpu_percent, virtual_memory, disk_usage
import platform
import subprocess

class SystemInformation(object):
    """
    System Informations for the index page.
    """
    def __init__(self):
        self.uptime = None
        self.uname = subprocess.check_output(['uname', '-a'], universal_newlines=True)  # Not necessary to reload
        self.distrib = None
        self.init_distrib()

    def init_distrib(self):
        distinfo = platform.linux_distribution()
        if distinfo == ('', '', ''):
            with open('/etc/lsb-release') as fd:
                for line in fd.readlines():
                    if line.find("DISTRIB_DESCRIPTION") >= 0:
                        self.distrib = line.split('"')[1]
            self.distrib = "Unknown"
        else:
            self.distrib = distinfo[0]

    def update(self):
        self.uptime = subprocess.check_output(['uptime'], universal_newlines=True)


def get_cpu_load():
    """ Returns the CPU Load """
    load = cpu_percent(interval=0, percpu=False)
    return load


def get_vmem():
    """ Returns the Ram percentage """
    mem = virtual_memory().percent
    return mem


def get_disk_usage():
    """ Returns the Disk usage """
    disk = disk_usage('/').percent
    return disk
