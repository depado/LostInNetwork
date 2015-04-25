# -*- coding: utf-8 -*-

import re
from app import app
from app import db
from app.models.vuln import VulnBasic


def vulnbasic():
    list_preco=open('data/source/preco.csv').readlines()
    app.logger.info('opening %s', app.config.get('list_preco'))
    for i in list_preco:
        x=i.split(';')
        preco = VulnBasic(match=(x[0]),expectmatch=(x[1]),description=(x[2]))
        preco.save()

if __name__ == '__vulnbasic__':
    vulnbasic()
