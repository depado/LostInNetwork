# -*- coding: utf-8 -*-

import celery

@celery.task(bind=True)
def scan_async(self):
    print("Ok !")
