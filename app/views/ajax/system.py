# -*- coding: utf-8 -*-

from flask import jsonify

from app.utils.system import get_cpu_load, get_disk_usage, get_vmem
from app import app


@app.route("/ajax/sys", methods=['GET', ])
def ajax_system():
    cpu = round(get_cpu_load())
    vmem = round(get_vmem())
    disk = round(get_disk_usage())
    return jsonify(cpu=cpu, vmem=vmem, disk=disk)
