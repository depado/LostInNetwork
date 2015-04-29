# -*- coding: utf-8 -*-

from flask import url_for

from app.models import Configuration, ConfVuln, VulnBasic, VulnCve


def generate_analysis_dict(device):
    """
    Configuration Dict :
    configuration_dict[device.name]['url'] (name + url)
    configuration_dict[device.name]['configurations'][
        [conf, conf, conf, ...], <- same date (last date)
        [conf, conf, conf, ...], <- older date
        [conf, conf, conf, ...], <- even older date
        ... <- etc, etc, etc
    ]
    """
    configuration_dict = dict()
    configuration_dict[device.name] = dict()
    configuration_dict[device.name]['url'] = url_for('inspect_device', device_id=device.id)
    configuration_dict[device.name]['configurations'] = list()
    previous = None
    for configuration in Configuration.query.filter_by(device=device).order_by(Configuration.date.desc()):
        truncated_date = configuration.date
        truncated_date = truncated_date.replace(hour=0, minute=0, second=0, microsecond=0)
        vuln_dict = dict(cve=list(), basic=list())
        for vuln in ConfVuln.query.filter(configuration.device == device).all():
            if vuln.vulnbasic_id:
                basic = VulnBasic.query.get(vuln.vulnbasic_id)
                if basic not in vuln_dict['basic']:
                    vuln_dict['basic'].append(basic)
            if vuln.vulncve_id:
                cve = VulnCve.query.get(vuln.vulncve_id)
                if cve not in vuln_dict['cve']:
                    vuln_dict['cve'].append(cve)
        if not previous or previous != truncated_date:
            configuration_dict[device.name]['configurations'].append([{'conf': configuration, 'vulns': vuln_dict}])
            previous = truncated_date
        else:
            configuration_dict[device.name]['configurations'][-1].append({'conf': configuration, 'vulns': vuln_dict})
    return configuration_dict
