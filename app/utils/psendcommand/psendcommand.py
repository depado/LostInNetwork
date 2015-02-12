# -*- coding: utf-8 -*-

import pexpect
from app import app

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
# PROMPT_REGEX_CISCO = "\r\n[\r]*[^\r\n\*># ]+[>#:][ ]*";
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
    'cisco': (PROMPT_REGEX_CISCO, PROMPT_REGEX_CISCOENABLE),
    'ciscoASA': (PROMPT_REGEX_CISCOASA, PROMPT_REGEX_CISCOENABLE)
}
ComCiscoISR = {'sh ip route': 'route', 'sh run': 'run'}


def send(data):
    directory = 'data/'
    derror = {}
    x = data.split(",")
    sMethod = (x[0])
    sHostname = (x[1])
    sIp = (x[2])
    sUsername = (x[3])
    sPassword = (x[4])
    sEnable = (x[5])
    sDeviceType = (x[6])

    if sMethod == "ssh":
        sTunnel = ('ssh -o ConnectTimeout=25 -o StrictHostKeyChecking=no -l ' + sDeviceType + ' ')
        app.logger.info(
            sHostname + 'connecting to ' + sUsername + '@' + sIp + ' ' + sHostname + ' whith ' + sMethod + ' and tunnel is ' + sTunnel)
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
        derror[sHostname] = 'TIMEOUT'
        return derror
    elif m == 2:
        derror[sHostname] = 'EOF'
        return derror
    q = child.expect(['>', '[Pp]assword:', pexpect.TIMEOUT, pexpect.EOF])
    if q == 0:
        child.sendline('enable')
    elif q == 1:
        derror[sHostname] = 'wrong password'
        return derror
    elif q == 2:
        derror[sHostname] = 'TIMEOUT'
        return derror
    elif q == 3:
        derror[sHostname] = 'EOF'
        return derror
    q = child.expect(['assword:', '>', pexpect.TIMEOUT, pexpect.EOF])
    if q == 0:
        child.sendline(sEnable)
    elif q == 1:
        child.sendline(sEnable)
    elif q == 2:
        derror[sHostname] = 'TIMEOUT'
        return derror
    elif q == 3:
        derror[sHostname] = 'EOF'
    if sDeviceType == "cisco":
        # q = child.expect (['#','>',pexpect.TIMEOUT,pexpect.EOF])
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
