# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import math
import os.path
import re
from typing import TYPE_CHECKING, Any

try:
    from wazo_provd import plugins, synchronize, tzinform
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
    from provd import plugins, synchronize, tzinform
    from provd.devices.config import RawConfigError
    from provd.devices.ident import RequestType
    from provd.devices.pgasso import BasePgAssociator, DeviceSupport
    from provd.plugins import FetchfwPluginHelper, StandardPlugin, TemplatePluginHelper
    from provd.servers.http import HTTPNoListingFileService
    from provd.servers.http_site import Request
    from provd.util import format_mac, norm_mac

from twisted.internet import defer

logger = logging.getLogger('plugin.wazo-fanvil')


if TYPE_CHECKING:
    from typing import TypedDict

    class FunctionKeyDict(TypedDict):
        label: str
        value: str
        line: str
        type: str

    class FKeyDict(TypedDict, total=False):
        id: int
        title: str
        type: int
        value: str


class BaseFanvilHTTPDeviceInfoExtractor:
    _PATH_REGEX = re.compile(r'\b(?!0{12})([\da-f]{12})\.cfg$')
    _UA_REGEX = re.compile(
        r'^Fanvil (?P<model>[XVi][0-9]{1,3}[WSGVUCi]?[DV]?[0-9]?(-V[12])?(\s?Pro)?) (?P<version>[0-9.]+) (?P<mac>[\da-f]{12})$'  # noqa: E501
    )

    def __init__(self, common_files):
        self._COMMON_FILES = common_files

    def extract(self, request: Request, request_type: RequestType):
        return defer.succeed(self._do_extract(request))

    def _do_extract(self, request: Request):
        dev_info = {}
        dev_info.update(self._extract_from_path(request))
        ua = request.getHeader(b'User-Agent')
        if ua:
            dev_info.update(self._extract_from_ua(ua.decode('ascii')))

        return dev_info

    def _extract_from_ua(self, ua: str):
        # Fanvil X4 2.10.2.6887 0c383e07e16c
        # Fanvil X6U Pro 0.0.10 0c383e2cd782
        # Fanvil V67 2.6.6.187 0c383e2b29e6
        # Fanvil i10SV 2.12.10.1 0c383e2397f4
        # Fanvil i53W 2.12.9 0c383e10a440
        # Fanvil V65 2.12.2.4 0c383e38e123
        # Fanvil H2U-V2 2.12.0 0c383e32342e

        dev_info = {}
        m = self._UA_REGEX.search(ua)
        if m:
            dev_info['vendor'] = 'Fanvil'
            dev_info['model'] = m.group('model').replace(' ', '-')
            dev_info['version'] = m.group('version')
            dev_info['mac'] = norm_mac(m.group('mac'))
        return dev_info

    def _extract_from_path(self, request: Request):
        filename = os.path.basename(request.path.decode('ascii'))
        device_info = self._COMMON_FILES.get(filename)
        if device_info:
            return {'vendor': 'Fanvil', 'model': device_info[0]}

        m = self._PATH_REGEX.search(request.path.decode('ascii'))
        if m:
            raw_mac = m.group(1)
            mac = norm_mac(raw_mac)
            return {'mac': mac}
        return {}


class BaseFanvilPgAssociator(BasePgAssociator):
    def __init__(self, models):
        super().__init__()
        self._models = models

    def _do_associate(
        self, vendor: str, model: str | None, version: str | None
    ) -> DeviceSupport:
        if vendor == 'Fanvil':
            if model in self._models:
                return DeviceSupport.COMPLETE
            return DeviceSupport.UNKNOWN
        return DeviceSupport.IMPROBABLE


class BaseFanvilPlugin(StandardPlugin):
    _ENCODING = 'UTF-8'
    _LOCALE: dict[str, str] = {}
    _COUNTRY = {
        'de_DE': '2',
        'en_CA': '18',
        'en_GB': '13',
        'en_US': '11',
        'es_ES': '33',
        'fr_CA': '18',
        'fr_FR': '25',
        'it_IT': '21',
        'nl_NL': '5',
    }
    _TZ_INFO: dict[int, list[tuple[str, int]]] = {}
    _SIP_DTMF_MODE = {
        'RTP-in-band': '0',
        'RTP-out-of-band': '1',
        'SIP-INFO': '2',
    }
    _SIP_TRANSPORT = {
        'udp': '0',
        'tcp': '1',
        'tls': '3',
    }
    _DIRECTORY_KEY = {
        'en': 'Directory',
        'fr': 'Annuaire',
    }
    _NEW_MODEL_REGEX = re.compile(r'^X([4-9][UC]|(210i?)|7)([- ]Pro)?$')
    _NEW_MODEL_SHORT_LANGUAGE_MAPPINGS = {
        'ca': 'cat',
        'eu': 'eus',
        'sk': 'slo',
    }
    _NEW_SUPPORTED_LANGUAGES = (
        'en',
        'cn',
        'tc',
        'ru',
        'it',
        'fr',
        'de',
        'he',
        'es',
        'cat',
        'eus',
        'tr',
        'hr',
        'slo',
        'cz',
        'nl',
        'ko',
        'ua',
        'pt',
        'pl',
        'ar',
    )

    _COMMON_FILES: dict[str, tuple[str, str, str]]
    _MODEL_FIRMWARE_MAPPING: dict[str, str]
    _FUNCTION_KEYS_PER_PAGE: dict[str, int]
    _LINE_KEYS_PER_PAGE: dict[str, int]
    _TOP_FUNCTION_KEYS: dict[str, int]
    _tftpboot_dir: str

    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        super().__init__(app, plugin_dir, gen_cfg, spec_cfg)
        # update to use the non-standard tftpboot directory
        self._base_tftpboot_dir = self._tftpboot_dir
        self._tftpboot_dir = os.path.join(self._tftpboot_dir, 'Fanvil')

        self._tpl_helper = TemplatePluginHelper(plugin_dir)

        downloaders = FetchfwPluginHelper.new_downloaders(gen_cfg.get('proxies'))
        fetchfw_helper = FetchfwPluginHelper(plugin_dir, downloaders)
        # update to use the non-standard tftpboot directory
        fetchfw_helper.root_dir = self._tftpboot_dir

        self.services = fetchfw_helper.services()
        self.http_service = HTTPNoListingFileService(self._base_tftpboot_dir)

    def _dev_specific_filename(self, device: dict[str, str]) -> str:
        # Return the device specific filename (not pathname) of device
        formatted_mac = format_mac(device['mac'], separator='', uppercase=False)
        return f'{formatted_mac}.cfg'

    def _check_config(self, raw_config: dict[str, Any]):
        if 'http_port' not in raw_config:
            raise RawConfigError('only support configuration via HTTP')

    def _check_device(self, device):
        if 'mac' not in device:
            raise Exception('MAC address needed for device configuration')

    def _add_wazo_phoned_user_service_url(self, raw_config: dict[str, Any], service):
        if hasattr(plugins, 'add_wazo_phoned_user_service_url'):
            plugins.add_wazo_phoned_user_service_url(raw_config, 'fanvil', service)

    def _add_server_url(self, raw_config: dict[str, Any]):
        if raw_config.get('http_base_url'):
            _, _, remaining_url = raw_config['http_base_url'].partition('://')
            raw_config['XX_server_url'] = raw_config['http_base_url']
            raw_config['XX_server_url_without_scheme'] = remaining_url
        else:
            base_url = f"{raw_config['ip']}:{raw_config['http_port']}"
            raw_config['XX_server_url_without_scheme'] = base_url
            raw_config['XX_server_url'] = f"http://{base_url}"

    def configure(self, device, raw_config: dict[str, Any]) -> None:
        self._check_config(raw_config)
        self._check_device(device)
        self._check_lines_password(raw_config)
        self._add_timezone(device, raw_config)
        self._add_locale(device, raw_config)
        self._add_sip_transport(raw_config)
        self._update_lines(raw_config)
        self._add_fkeys(device, raw_config)
        self._add_phonebook_url(raw_config)
        self._add_phonebook_url_v2(raw_config)
        self._add_wazo_phoned_user_service_url(raw_config, 'dnd')
        self._add_server_url(raw_config)
        self._add_firmware(device, raw_config)

        filename = self._dev_specific_filename(device)
        tpl = self._tpl_helper.get_dev_template(filename, device)

        path = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, raw_config, path, self._ENCODING)

    def deconfigure(self, device) -> None:
        self._remove_configuration_file(device)

    def configure_common(self, raw_config: dict[str, Any]) -> None:
        self._add_server_url(raw_config)
        for filename, (
            model_info,
            fw_filename,
            tpl_filename,
        ) in self._COMMON_FILES.items():
            tpl = self._tpl_helper.get_template(f'common/{tpl_filename}')
            dst = os.path.join(self._tftpboot_dir, filename)
            raw_config['XX_fw_filename'] = fw_filename
            raw_config['XX_model_info'] = model_info
            self._tpl_helper.dump(tpl, raw_config, dst, self._ENCODING)

    def _remove_configuration_file(self, device):
        path = os.path.join(self._tftpboot_dir, self._dev_specific_filename(device))
        try:
            os.remove(path)
        except OSError as e:
            logger.info('error while removing configuration file: %s', e)

    def synchronize(self, device, raw_config: dict[str, Any]):
        return synchronize.standard_sip_synchronize(device)

    def get_remote_state_trigger_filename(self, device):
        if 'mac' not in device:
            return None

        return self._dev_specific_filename(device)

    def _check_lines_password(self, raw_config: dict[str, Any]):
        for line in raw_config['sip_lines'].values():
            if line['password'] == 'autoprov':
                line['password'] = ''

    def _extract_dst_change(self, dst_change):
        lines = {
            'month': dst_change['month'],
            'hour': min(dst_change['time'].as_hours, 23),
        }
        if dst_change['day'].startswith('D'):
            lines['dst_wday'] = dst_change['day'][1:]
        else:
            week, weekday = dst_change['day'][1:].split('.')
            if week == '5':
                lines['dst_week'] = -1
            else:
                lines['dst_week'] = week
            lines['dst_wday'] = int(weekday) - 1
        return lines

    def _extract_tzinfo(self, device, tzinfo):
        tz_all: dict[str, Any] = {}
        utc: int = tzinfo['utcoffset'].as_hours
        utc_list = self._TZ_INFO[utc]
        for time_zone_name, time_zone in utc_list:
            tz_all['time_zone'] = time_zone
            tz_all['time_zone_name'] = time_zone_name

        if tzinfo['dst'] is None:
            tz_all['enable_dst'] = False
        else:
            tz_all['enable_dst'] = True
            tz_all['dst_min_offset'] = min(tzinfo['dst']['save'].as_minutes, 60)
            tz_all['dst_start'] = self._extract_dst_change(tzinfo['dst']['start'])
            tz_all['dst_end'] = self._extract_dst_change(tzinfo['dst']['end'])
        return tz_all

    def _add_timezone(self, device, raw_config: dict[str, Any]):
        if 'timezone' in raw_config:
            try:
                tzinfo = tzinform.get_timezone_info(raw_config['timezone'])
            except tzinform.TimezoneNotFoundError as e:
                logger.info('Unknown timezone: %s', e)
            else:
                raw_config['XX_timezone'] = self._extract_tzinfo(device, tzinfo)

    def _is_new_model(self, device):
        return self._NEW_MODEL_REGEX.match(device.get('model', '')) is not None

    def _add_locale(self, device, raw_config: dict[str, Any]):
        locale = raw_config.get('locale')
        if not locale:
            return
        raw_config['XX_country'] = self._COUNTRY.get(locale, self._COUNTRY['en_US'])
        language = locale.split('_')[0]
        if self._is_new_model(device):
            language = self._NEW_MODEL_SHORT_LANGUAGE_MAPPINGS.get(language, language)
            if language in self._NEW_SUPPORTED_LANGUAGES:
                raw_config['XX_locale'] = language
        elif locale in self._LOCALE:
            raw_config['XX_locale'] = self._LOCALE[locale]
        directory_key_text = self._DIRECTORY_KEY.get(language, None)
        if directory_key_text:
            raw_config['XX_directory'] = directory_key_text

    def _update_lines(self, raw_config: dict[str, Any]):
        default_dtmf_mode = raw_config.get('sip_dtmf_mode', 'SIP-INFO')
        for line in raw_config['sip_lines'].values():
            line['XX_dtmf_mode'] = self._SIP_DTMF_MODE[
                line.get('dtmf_mode', default_dtmf_mode)
            ]
            line['backup_proxy_ip'] = line.get('backup_proxy_ip') or raw_config.get(
                'sip_backup_proxy_ip'
            )
            line['backup_proxy_port'] = line.get('backup_proxy_port') or raw_config.get(
                'sip_backup_proxy_port'
            )
            if 'voicemail' not in line and 'exten_voicemail' in raw_config:
                line['voicemail'] = raw_config['exten_voicemail']

    def _add_sip_transport(self, raw_config: dict[str, Any]) -> None:
        raw_config['X_sip_transport_protocol'] = self._SIP_TRANSPORT[
            raw_config.get('sip_transport', 'udp')
        ]

    def _format_funckey_speeddial(self, funckey_dict: FunctionKeyDict) -> str:
        return f'{funckey_dict["value"]}@{funckey_dict["line"]}/f'

    def _format_funckey_blf(
        self, funckey_dict: FunctionKeyDict, exten_pickup_call=None
    ) -> str:
        # Be warned that blf works only for DSS keys.
        blf_entry = f'{funckey_dict["value"]}@{funckey_dict["line"]}/ba'
        if exten_pickup_call:
            return f'{blf_entry}{exten_pickup_call}{funckey_dict["value"]}'
        return blf_entry

    def _format_funckey_call_park(self, funckey_dict: FunctionKeyDict) -> str:
        return f'{funckey_dict["value"]}@{funckey_dict["line"]}/c'

    @staticmethod
    def _split_fkeys(
        funckeys: list[tuple[str, FunctionKeyDict]], threshold: int
    ) -> tuple[dict[int, FunctionKeyDict], dict[int, FunctionKeyDict]]:
        fkeys_top: dict[int, FunctionKeyDict] = {}
        fkeys_bottom: dict[int, FunctionKeyDict] = {}

        for funckey_no, funckey_dict in funckeys:
            keynum = int(funckey_no)
            if keynum <= threshold:
                fkeys_top[keynum] = funckey_dict
            else:
                fkeys_bottom[keynum - threshold] = funckey_dict
        return fkeys_top, fkeys_bottom

    def _format_fkey(
        self,
        funckey_number: int,
        funckey: FunctionKeyDict,
        fkey_offset: int,
        pickup_exten: str | None,
    ) -> FKeyDict:
        fkey: FKeyDict = {'id': funckey_number, 'title': funckey['label'], 'type': 2}
        if funckey['type'] == 'speeddial':
            fkey['type'] = 1
            fkey['value'] = self._format_funckey_speeddial(funckey)
        elif funckey['type'] == 'blf':
            fkey['type'] = 1
            fkey['value'] = self._format_funckey_blf(funckey, pickup_exten)
        elif funckey['type'] == 'park':
            fkey['value'] = self._format_funckey_call_park(funckey)
        else:
            logger.info('Unsupported funckey type: %s', funckey['type'])
            fkey['type'] = 0
        return fkey

    def _format_fkeys(
        self,
        fkeys: dict[int, FunctionKeyDict],
        max_fkeys: int,
        offset: int,
        exten_pickup_call: str | None,
    ) -> list[FKeyDict]:
        formatted_fkeys = []
        for fkey_num in range(1, max_fkeys + 1):
            fkey: FunctionKeyDict | None = fkeys.get(fkey_num)
            if not fkey:
                fkey = {'id': fkey_num, 'label': '', 'type': None}  # type: ignore
            formatted_fkeys.append(
                self._format_fkey(fkey_num, fkey, offset, exten_pickup_call)  # type: ignore
            )
        return formatted_fkeys

    def _add_fkeys(self, device, raw_config: dict[str, Any]):
        exten_pickup_call: str | None = raw_config.get('exten_pickup_call')
        offset = 0 if self._is_new_model(device) else 1
        raw_config['XX_offset'] = offset
        clean_model_name = device.get('model', '').split('-')[0]
        top_key_threshold = self._TOP_FUNCTION_KEYS.get(clean_model_name, 0)
        raw_config['XX_top_key_threshold'] = top_key_threshold
        top_keys, bottom_keys = self._split_fkeys(
            raw_config['funckeys'].items(), top_key_threshold
        )

        raw_config['XX_top_keys'] = top_keys
        raw_config['XX_bottom_keys'] = bottom_keys

        top_keys_per_page = self._LINE_KEYS_PER_PAGE.get(clean_model_name, None)
        keys_per_page = self._FUNCTION_KEYS_PER_PAGE.get(clean_model_name, None)

        max_top_keys = max(top_keys) if top_keys else 0
        max_bottom_keys = max(bottom_keys) if bottom_keys else 0
        formatted_top_keys = self._format_fkeys(
            top_keys, max_top_keys, offset, exten_pickup_call
        )
        formatted_bottom_keys = self._format_fkeys(
            bottom_keys, max_bottom_keys, offset, exten_pickup_call
        )
        if top_keys_per_page:
            max_top_page, paginated_top_fkeys = self._paginate(
                formatted_top_keys, max_top_keys, top_keys_per_page
            )
            raw_config['XX_max_top_page'] = max_top_page
            raw_config['XX_paginated_top_fkeys'] = paginated_top_fkeys
        else:
            raw_config['XX_paginated_top_fkeys'] = [
                (offset, fkey['id'] + offset, fkey) for fkey in formatted_top_keys
            ]

        if keys_per_page:
            max_bottom_page, paginated_bottom_fkeys = self._paginate(
                formatted_bottom_keys, max_bottom_keys, keys_per_page
            )
            raw_config['XX_max_page'] = max_bottom_page
            raw_config['XX_paginated_fkeys'] = paginated_bottom_fkeys
        raw_config['XX_fkeys'] = formatted_top_keys + formatted_bottom_keys

    @staticmethod
    def _paginate(
        fkeys: list[FKeyDict], max_position: int, results_per_page: int
    ) -> tuple[int, list[tuple[int, int, FKeyDict]]]:
        max_page = math.ceil(max_position / results_per_page)
        paginated_fkeys = sorted(
            [
                (
                    ((fkey['id'] - 1) // results_per_page) + 1,
                    ((fkey['id'] - 1) % results_per_page) + 1,
                    fkey,
                )
                for fkey in fkeys
            ]
        )
        return max_page, paginated_fkeys

    def _add_phonebook_url(self, raw_config: dict[str, Any]) -> None:
        if (
            hasattr(plugins, 'add_xivo_phonebook_url')
            and raw_config.get('config_version', 0) >= 1
        ):
            plugins.add_xivo_phonebook_url(
                raw_config, 'fanvil', entry_point='lookup', qs_suffix='term='
            )

    def _add_phonebook_url_v2(self, raw_config: dict[str, Any]) -> None:
        if (
            hasattr(plugins, 'add_xivo_phonebook_url')
            and raw_config.get('config_version', 0) >= 1
        ):
            original_phonebook_url = raw_config.get('XX_xivo_phonebook_url')
            if not original_phonebook_url:
                return

            plugins.add_xivo_phonebook_url(
                raw_config, 'fanvil-v2', entry_point='lookup', qs_suffix='term=#'
            )
            fixed_url = raw_config['XX_xivo_phonebook_url'].replace('&', '&amp;')

            raw_config['XX_wazo_phonebook_url_v2'] = fixed_url
            raw_config['XX_xivo_phonebook_url'] = original_phonebook_url

    def _add_firmware(self, device, raw_config: dict[str, Any]) -> None:
        model = device.get('model')
        if model in self._MODEL_FIRMWARE_MAPPING:
            raw_config['XX_fw_filename'] = self._MODEL_FIRMWARE_MAPPING[model]
