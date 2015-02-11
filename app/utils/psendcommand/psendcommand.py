# -*- coding: utf-8 -*-

import pexpect
from app import app

PROMPT_REGEX_DEBIAN = "\r\n[^\r\n ]+:[^\r\n]+[\\\$#][ ]*"  # 20121312-YRG:
PROMPT_REGEX_IPSO = "\r\n[^\r\n ]+\\\[[^\r\n]+\\\]#[ ]*"  # 20121312-YRG:
PROMPT_REGEX_SPLAT = "\r\n\\\[[^\r\n ]+@[^\r\n]+\\\]#[ ]*"  # 20121312-YRG
PROMPT_REGEX_REDHAT = "\r\n\\\[[^\r\n ]+@[^\r\n]+\\\][\\\$#][ ]*"  # 20121
PROMPT_REGEX_JUNOS = "\r\n[^\r\n ]+@[^\r\n]+[\\\]>[ ]*"
PROMPT_REGEX_JUNOSEDIT = "\r\n[^\r\n ]+@[^\r\n]+[\\\]#[ ]*"
#PROMPT_REGEX_GENTOO = "[^\n]+@[^\n]+ [^\n]+ \\\$|[^\n]+ [^\n]+ #";
#PROMPT_REGEX_POSIX = PROMPT_REGEX_DEBIAN.'|'.PROMPT_REGEX_IPSO.'|'.PROMPT_REGEX_SPLAT.'|'.PROMPT_REGEX_REDHAT;
PROMPT_REGEX_BLUECOAT = "\r\n[^\r\n ]+>[ ]*"  # 20121312-YRG: need to veri
PROMPT_REGEX_BLUECOATENABLE = "\r\n[^\r\n ]+#[ ]*"  # 20121312-YRG: need t
PROMPT_REGEX_BLUECOATCONFIG = "\r\n[^\r\n ]+#([^)]+)[ ]*"  # 20121312-YRG:
#PROMPT_REGEX_CISCO = "\r\n[\r]*[^\r\n\*># ]+[>#:][ ]*"
PROMPT_REGEX_CISCO = ".*[>#:][ ]*"  # 20152701-ALD
PROMPT_REGEX_CISCOASA = "\r\n\r[^\r\n\*># ]+[>#] "
PROMPT_REGEX_CISCOENABLE = "\r\n[\r]*[^\r\n\*# ]+#[ ]*"
PROMPT_REGEX_NETSCREEN = "\r\n[^\r\n ]+([^\r\n ]+)->[ ]*"  # 20121312-YRG
#PROMPT_REGEX_TIPPINGPOINT = "\r\n[^\r\n ]+#"
PROMPT_REGEX_TIPPINGPOINT = "[\r\n]+[^\r\n ]+#[ ]*"  #TippingPoint is
PROMPT_REGEX_IRONPORT = "\r\n[\r]*[^\r\n\*># ]+>[ ]*"
PROMPT_REGEX_NETSCALER = "\r\n[\r]*>[ ]*"

#Definition command to send depend to the devicetype

Regex = {
    'cisco': (PROMPT_REGEX_CISCO, PROMPT_REGEX_CISCOENABLE),
    'ciscoASA': (PROMPT_REGEX_CISCOASA,PROMPT_REGEX_CISCOENABLE)
}

ComCiscoISR = {
    'sh ip route': 'route',
    'sh run': 'run'
}

debug = app.config['DEBUG']

def send(data):
    adict = dict()
    derror = {}
    x=data.split (",")
    s_method = (x[0])
    s_hostname = (x[1])
    s_ip = (x[2])
    s_username = (x[3])
    s_password = (x[4])
    s_enable = (x[5])
    s_device_type = (x[6])

    if s_method == "ssh":
        # sTunnel = ('ssh -o StrictHostKeyChecking=no -l ' + sUID + ' ')
        s_tunnel = ('ssh -o ConnectTimeout=25 -o StrictHostKeyChecking=no -l ' + s_device_type + ' ')
        if debug:
            print('Connecting to ' + s_username + '@' + s_ip + ' ' + s_hostname + ' whith ' + s_method + ' and tunnel is ' + s_tunnel)
        child = pexpect.spawn(s_tunnel + s_username + '@' + s_ip)
    elif s_method == "telnet":
        s_tunnel = 'telnet '
        if debug:
            print('Connecting to ' + s_ip + ' ' + s_hostname + ' whith ' + s_method + ' and tunnel is ' + s_tunnel)
        child = pexpect.spawn(s_tunnel + s_ip)
        m = child.expect ([PROMPT_REGEX_CISCO, pexpect.TIMEOUT, pexpect.EOF])
        if m == 0:
            child.sendline(s_username)
            if app.config['DEBUG']:
                print('child.sendline sUsername')
        elif m == 1:
            if debug:
                print('TIMEOUT')
            return
        elif m == 2:
            if debug:
                print('EOF')
            return
    else:
        return
    m = child.expect ([PROMPT_REGEX_CISCO, 'assword:', pexpect.TIMEOUT, pexpect.EOF])
    if m == 0:
        child.sendline(s_password)
        if debug:
            print('child.sendline sPassword')
    elif m == 1:
        adict[s_hostname] = 'TIMEOUT'
        if debug:
            print("TIMEOUT")
        return
    elif m == 2:
        adict[s_hostname]='EOF'
        print ("EOF")
        return
    q = child.expect (['>', '[Pp]assword:', pexpect.TIMEOUT, pexpect.EOF])
    if q == 0:
        child.sendline ('enable')
    elif q == 1:
        adict[s_hostname]='wrong password'
        print ('wrong password')
        return
    elif q == 2:
        adict[s_hostname]='TIMEOUT'
        print ('TIMEOUT')
        return
    elif q == 3:
        adict[s_hostname]='EOF'
        print ('EOF')
        return
    q = child.expect (['assword:', '>', pexpect.TIMEOUT,pexpect.EOF])
    if q == 0:
        child.sendline (s_enable)
    elif q == 1:
        child.sendline (s_enable)
    elif q == 2:
        adict[s_hostname]='TIMEOUT'
        print ('TIMEOUT')
        return
    elif q == 3:
        adict[s_hostname]='EOF'
        print ('EOF')
    if s_device_type == "cisco":
        #q = child.expect (['#','>',pexpect.TIMEOUT,pexpect.EOF])
        q = child.expect ([PROMPT_REGEX_CISCOENABLE,'>',pexpect.TIMEOUT,pexpect.EOF])
        if q==0:
            child.sendline ('terminal length 0')
        elif q == 1:
            adict[s_hostname]='wrong enable password'
            print ('Wrong enable password')
            return
        elif q == 2:
            print ('TIMEOUT')
            return
        elif q == 3:
            print ('EOF')
            return
        q = child.expect ([PROMPT_REGEX_CISCOENABLE,pexpect.TIMEOUT,pexpect.EOF])
        for key in ComCiscoISR:
            if debug:
                print(key)
            if q == 0:
                print('child.sendline '+ key) 
                child.sendline (key)
            elif q == 1:
                print ('TIMEOUT')
                return
            elif q == 2:
                print ('EOF')
                return
            q = child.expect ([PROMPT_REGEX_CISCOENABLE, pexpect.TIMEOUT, pexpect.EOF])
            with open(s_hostname +'-' + ComCiscoISR[key] + '.txt', 'wb') as fd:
                fd.write(child.before)
        child.sendline('exit')
        return adict
