# Copyright 2010-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import logging
import os.path
import re

try:
    from wazo_provd import synchronize
    from wazo_provd.devices.config import RawConfigError
    from wazo_provd.devices.ident import RequestType
    from wazo_provd.devices.pgasso import BasePgAssociator, DeviceSupport
    from wazo_provd.plugins import (
        FetchfwPluginHelper,
        StandardPlugin,
        TemplatePluginHelper,
    )
    from wazo_provd.servers.http import HTTPNoListingFileService
    from wazo_provd.servers.http_site import Request
    from wazo_provd.util import format_mac, norm_mac
except ImportError:
    # Compatibility with wazo < 24.02
    from provd import synchronize
    from provd.devices.config import RawConfigError
    from provd.devices.ident import RequestType
    from provd.devices.pgasso import BasePgAssociator, DeviceSupport
    from provd.plugins import FetchfwPluginHelper, StandardPlugin, TemplatePluginHelper
    from provd.servers.http import HTTPNoListingFileService
    from provd.servers.http_site import Request
    from provd.util import format_mac, norm_mac

from twisted.internet import defer

logger = logging.getLogger('plugin.wazo-grandstream')

TZ_NAME = {'Europe/Paris': 'CET-1CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00'}
LOCALE = {
    'de_DE': 'de',
    'es_ES': 'es',
    'fr_FR': 'fr',
    'fr_CA': 'fr',
    'it_IT': 'it',
    'nl_NL': 'nl',
    'en_US': 'en',
}

FUNCKEY_TYPES = {
    'speeddial': 'SpeedDial',
    'blf': 'BLF',
    'park': 'CallPark',
    'default': 'Line',
    'disabled': 'None',
}


class BaseGrandstreamHTTPDeviceInfoExtractor:
    # Grandstream Model HW GXP1405 SW 1.0.4.23 DevId 000b8240d55c
    # Grandstream Model HW GXP1628 SW 1.0.4.138 DevId c074ad2bd859
    # Grandstream Model HW GXP2200 V2.2A SW 1.0.1.33 DevId 000b82462d97
    # Grandstream Model HW GXV3240 V1.6B SW 1.0.1.27 DevId 000b82632815
    # Grandstream Model HW GXV3350  V1.3A SW 1.0.1.8 DevId c074ad150b88
    # Grandstream GXP2000 (gxp2000e.bin:1.2.5.3/boot55e.bin:1.1.6.9) DevId 000b822726c8
    # Grandstream Model HW GRP2614 SW 1.0.5.15 DevId c074ad0b63ee
    # Grandstream Model HW HT801 V1.1A SW 1.0.17.5 DevId c074ad273a10

    _UA_REGEX_LIST = [
        re.compile(
            r'^Grandstream Model HW (\w+)(?:\s+V[^ ]+)? SW ([^ ]+) DevId ([^ ]+)'
        ),
        re.compile(r'^Grandstream (GXP2000) .*:([^ ]+)\) DevId ([^ ]+)'),
    ]

    def extract(self, request: Request, request_type: RequestType):
        return defer.succeed(self._do_extract(request))

    def _do_extract(self, request: Request):
        ua = request.getHeader(b'User-Agent')
        if ua:
            return self._extract_from_ua(ua.decode('ascii'))

    def _extract_from_ua(self, ua: str):
        for UA_REGEX in self._UA_REGEX_LIST:
            m = UA_REGEX.match(ua)
            if m:
                raw_model, raw_version, raw_mac = m.groups()
                try:
                    mac = norm_mac(raw_mac)
                except ValueError as e:
                    logger.warning(
                        'Could not normalize MAC address "%s": %s', raw_mac, e
                    )
                else:
                    return {
                        'vendor': 'Grandstream',
                        'model': raw_model,
                        'version': raw_version,
                        'mac': mac,
                    }


class BaseGrandstreamPgAssociator(BasePgAssociator):
    def __init__(self, models, version):
        super().__init__()
        self._models = models
        self._version = version

    def _do_associate(
        self, vendor: str, model: str | None, version: str | None
    ) -> DeviceSupport:
        if vendor == 'Grandstream':
            if model in self._models:
                if version and version.startswith(self._version):
                    return DeviceSupport.EXACT
                return DeviceSupport.COMPLETE
            return DeviceSupport.UNKNOWN
        return DeviceSupport.IMPROBABLE


class BaseGrandstreamPlugin(StandardPlugin):
    _ENCODING = 'UTF-8'
    # VPKs are the virtual phone keys on the main display
    # MPKs are the physical programmable keys on some models
    MODEL_FKEYS = {
        'GRP2612': {
            'vpk': 16,
            'mpk': 0,
        },
        'GRP2613': {
            'vpk': 24,
            'mpk': 0,
        },
        'GRP2614': {
            'vpk': 16,
            'mpk': 24,
        },
        'GRP2615': {
            'vpk': 40,
            'mpk': 0,
        },
        'GRP2616': {
            'vpk': 16,
            'mpk': 24,
        },
        'GXP2130': {
            'vpk': 12,
            'mpk': 8,
        },
        'GXP2135': {
            'vpk': 32,
            'mpk': 0,
        },
        'GXP2140': {
            'vpk': 16,
            'mpk': 0,
        },
        'GXP2160': {
            'vpk': 24,
            'mpk': 24,
        },
        'GXP2170': {
            'vpk': 48,
            'mpk': 0,
        },
    }

    DTMF_MODES = {
        # mode: (in audio, in RTP, in SIP)
        'RTP-in-band': ('Yes', 'Yes', 'No'),
        'RTP-out-of-band': ('No', 'Yes', 'No'),
        'SIP-INFO': ('No', 'No', 'Yes'),
    }

    SIP_TRANSPORTS = {
        'udp': 'UDP',
        'tcp': 'TCP',
        'tls': 'TlsOrTcp',
    }
    _tftpboot_dir: str

    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        super().__init__(app, plugin_dir, gen_cfg, spec_cfg)
        # update to use the non-standard tftpboot directory
        self._base_tftpboot_dir = self._tftpboot_dir
        self._tftpboot_dir = os.path.join(self._tftpboot_dir, 'Grandstream')

        self._tpl_helper = TemplatePluginHelper(plugin_dir)

        downloaders = FetchfwPluginHelper.new_downloaders(gen_cfg.get('proxies'))
        fetchfw_helper = FetchfwPluginHelper(plugin_dir, downloaders)
        # update to use the non-standard tftpboot directory
        fetchfw_helper.root_dir = self._tftpboot_dir

        self.services = fetchfw_helper.services()
        self.http_service = HTTPNoListingFileService(self._base_tftpboot_dir)

    http_dev_info_extractor = BaseGrandstreamHTTPDeviceInfoExtractor()

    def _dev_specific_filename(self, device: dict[str, str]) -> str:
        # Return the device specific filename (not pathname) of device
        formatted_mac = format_mac(device['mac'], separator='', uppercase=False)
        return f'cfg{formatted_mac}.xml'

    def _check_config(self, raw_config):
        if 'http_port' not in raw_config:
            raise RawConfigError('only support configuration via HTTP')

    def _check_device(self, device):
        if 'mac' not in device:
            raise Exception('MAC address needed for device configuration')

    def configure(self, device, raw_config):
        self._check_config(raw_config)
        self._check_device(device)
        self._check_lines_password(raw_config)
        self._add_sip_transport(raw_config)
        self._add_timezone(raw_config)
        self._add_locale(raw_config)
        self._add_dtmf_mode(raw_config)
        self._add_fkeys(raw_config)
        self._add_mpk(raw_config)
        self._add_v2_fkeys(raw_config, device.get('model'))
        self._add_dns(raw_config)
        filename = self._dev_specific_filename(device)
        tpl = self._tpl_helper.get_dev_template(filename, device)

        path = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, raw_config, path, self._ENCODING)

    def deconfigure(self, device):
        self._remove_configuration_file(device)

    def _remove_configuration_file(self, device):
        path = os.path.join(self._tftpboot_dir, self._dev_specific_filename(device))
        try:
            os.remove(path)
        except OSError as e:
            logger.info('error while removing configuration file: %s', e)

    def synchronize(self, device, raw_config):
        return synchronize.standard_sip_synchronize(device)

    def get_remote_state_trigger_filename(self, device):
        if 'mac' in device:
            return self._dev_specific_filename(device)

    def _check_lines_password(self, raw_config):
        for line in raw_config['sip_lines'].values():
            if line['password'] == 'autoprov':
                line['password'] = ''

    def _add_timezone(self, raw_config):
        if 'timezone' in raw_config and raw_config['timezone'] in TZ_NAME:
            raw_config['XX_timezone'] = TZ_NAME[raw_config['timezone']]
        else:
            raw_config['timezone'] = TZ_NAME['Europe/Paris']

    def _add_locale(self, raw_config):
        locale = raw_config.get('locale')
        if locale in LOCALE:
            raw_config['XX_locale'] = LOCALE[locale]

    def _add_fkeys(self, raw_config):
        lines: list[tuple[str, str | int]] = []
        for funckey_no, funckey_dict in raw_config['funckeys'].items():
            i_funckey_no = int(funckey_no)
            funckey_type = funckey_dict['type']
            if funckey_type not in FUNCKEY_TYPES:
                logger.info('Unsupported funckey type: %s', funckey_type)
                continue
            type_code = f'P32{i_funckey_no + 2}'
            lines.append((type_code, FUNCKEY_TYPES[funckey_type]))
            line_code = self._format_code(3 * i_funckey_no - 2)
            lines.append((line_code, int(funckey_dict['line']) - 1))
            if 'label' in funckey_dict:
                label_code = self._format_code(3 * i_funckey_no - 1)
                lines.append((label_code, funckey_dict['label']))
            value_code = self._format_code(3 * i_funckey_no)
            lines.append((value_code, funckey_dict['value']))
        raw_config['XX_fkeys'] = lines

    def _add_mpk(self, raw_config):
        lines: list[tuple[str, int | str]] = []
        start_code = 23000
        for funckey_no, funckey_dict in raw_config['funckeys'].items():
            i_funckey_no = int(funckey_no)  # starts at 1
            funckey_type = funckey_dict['type']
            if funckey_type not in FUNCKEY_TYPES:
                logger.info('Unsupported funckey type: %s', funckey_type)
                continue
            start_p_code = start_code + (i_funckey_no - 1) * 5
            type_code = f'P{start_p_code}'
            lines.append((type_code, FUNCKEY_TYPES[funckey_type]))
            line_code = f'P{start_p_code + 1}'
            lines.append((line_code, int(funckey_dict['line']) - 1))
            if 'label' in funckey_dict:
                label_code = f'P{start_p_code + 2}'
                lines.append((label_code, funckey_dict['label']))
            value_code = f'P{start_p_code + 3}'
            lines.append((value_code, funckey_dict['value']))
        raw_config['XX_mpk'] = lines

    def _add_v2_fkeys(self, raw_config, model):
        lines = []
        model_fkeys = self.MODEL_FKEYS.get(model)
        if not model_fkeys:
            logger.info('Unknown model: "%s"', model)
            return
        for funckey_no in range(1, model_fkeys['vpk'] + 1):
            funckey = raw_config['funckeys'].get(str(funckey_no), {})
            funckey_type = funckey.get('type', 'disabled')
            if funckey_type not in FUNCKEY_TYPES:
                logger.info('Unsupported funckey type: %s', funckey_type)
                continue
            if str(funckey_no) in raw_config['sip_lines']:
                logger.info(
                    'Function key %s would conflict with an existing line', funckey_no
                )
                continue
            lines.append(
                (
                    funckey_no,
                    {
                        'section': 'vpk',
                        'type': FUNCKEY_TYPES[funckey_type],
                        'label': funckey.get('label') or '',
                        'value': funckey.get('value') or '',
                    },
                )
            )
        for funckey_no in range(1, model_fkeys['mpk'] + 1):
            funckey = raw_config['funckeys'].get(
                str(funckey_no + model_fkeys['vpk']), {}
            )
            funckey_type = funckey.get('type', 'disabled')
            if funckey_type not in FUNCKEY_TYPES:
                logger.info('Unsupported funckey type: %s', funckey_type)
            lines.append(
                (
                    funckey_no,
                    {
                        'section': 'mpk',
                        'type': FUNCKEY_TYPES[funckey_type],
                        'label': funckey.get('label') or '',
                        'value': funckey.get('value') or '',
                    },
                )
            )
        raw_config['XX_v2_fkeys'] = lines

    def _format_code(self, code):
        if code >= 10:
            str_code = str(code)
        else:
            str_code = f'0{code}'
        return f'P3{str_code}'

    def _add_dns(self, raw_config):
        if raw_config.get('dns_enabled'):
            dns_parts = raw_config['dns_ip'].split('.')
            for part_nb, part in enumerate(dns_parts, start=1):
                raw_config[f'XX_dns_{part_nb}'] = part

    def _add_dtmf_mode(self, raw_config):
        if raw_config.get('sip_dtmf_mode'):
            dtmf_info = self.DTMF_MODES[raw_config['sip_dtmf_mode']]
            raw_config['XX_dtmf_in_audio'] = dtmf_info[0]
            raw_config['XX_dtmf_in_rtp'] = dtmf_info[1]
            raw_config['XX_dtmf_in_sip'] = dtmf_info[2]

    def _add_sip_transport(self, raw_config):
        sip_transport = raw_config.get('sip_transport')
        if sip_transport in self.SIP_TRANSPORTS:
            raw_config['XX_sip_transport'] = self.SIP_TRANSPORTS[sip_transport]
