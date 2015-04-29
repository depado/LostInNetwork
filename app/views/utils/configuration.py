# -*- coding: utf-8 -*-

from flask import url_for

from app.models import Configuration

def generate_conf_dict(device):
    configuration_dict = dict()
    configuration_dict[device.name] = dict()
    configuration_dict[device.name]['url'] = url_for('inspect_device', device_id=device.id)
    configuration_dict[device.name]['configurations'] = list()
    previous = None
    for configuration in Configuration.query.filter_by(device=device).order_by(Configuration.date.desc()):
        truncated_date = configuration.date
        truncated_date = truncated_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if not previous or previous != truncated_date:
            configuration_dict[device.name]['configurations'].append([configuration])
            previous = truncated_date
        else:
            configuration_dict[device.name]['configurations'][-1].append(configuration)
    return configuration_dict
