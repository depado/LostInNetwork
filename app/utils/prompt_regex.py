# -*- coding: utf-8 -*-

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
PROMPT_REGEX_CISCO = "\r\n[\r]*[^\r\n\*># ]+[>#:][ ]*"
PROMPT_REGEX_CISCOASA = "\r\n\r[^\r\n\*># ]+[>#] "
PROMPT_REGEX_CISCOENABLE = "\r\n[\r]*[^\r\n\*# ]+#[ ]*"
PROMPT_REGEX_NETSCREEN = "\r\n[^\r\n ]+([^\r\n ]+)->[ ]*"  # 20121312-YRG
# PROMPT_REGEX_TIPPINGPOINT = "\r\n[^\r\n ]+#";
PROMPT_REGEX_TIPPINGPOINT = "[\r\n]+[^\r\n ]+#[ ]*"  # TippingPoint is
PROMPT_REGEX_IRONPORT = "\r\n[\r]*[^\r\n\*># ]+>[ ]*"
PROMPT_REGEX_NETSCALER = "\r\n[\r]*>[ ]*"

Regex = {
    'Cisco': (PROMPT_REGEX_CISCO, PROMPT_REGEX_CISCOENABLE),
    'ciscoASA': (PROMPT_REGEX_CISCOASA, PROMPT_REGEX_CISCOENABLE)
}
