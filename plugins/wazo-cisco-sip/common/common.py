# -*- coding: utf-8 -*-

# Copyright (C) 2018 Wazo Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
import os
import re
from provd import plugins
from provd import tzinform
from provd.devices.config import RawConfigError
from provd.devices.pgasso import BasePgAssociator, IMPROBABLE_SUPPORT, \
    NO_SUPPORT, COMPLETE_SUPPORT, PROBABLE_SUPPORT
from provd.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from provd.servers.http import HTTPNoListingFileService
from provd.servers.tftp.service import TFTPFileService
from provd import synchronize
from provd.util import norm_mac, format_mac
from twisted.internet import defer

logger = logging.getLogger('plugin.wazo-cisco-sip')


class BaseCiscoPgAssociator(BasePgAssociator):
    def __init__(self, models):
        self._models = models

    def _do_associate(self, vendor, model, version):
        if vendor == u'Cisco':
            if model is None:
                # when model is None, give a score slightly higher than
                # xivo-cisco-spa plugins
                return PROBABLE_SUPPORT + 10
            if model.startswith(u'SPA'):
                return NO_SUPPORT
            if model.startswith(u'ATA'):
                return NO_SUPPORT
            if model in self._models:
                return COMPLETE_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT


class BaseCiscoDHCPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        return defer.succeed(self._do_extract(request))

    _VDI_REGEX = re.compile(r'\bPhone (?:79(\d\d)|CP-79(\d\d)G|CP-(\d\d\d\d))')

    def _do_extract(self, request):
        options = request[u'options']
        if 60 in options:
            return self._extract_from_vdi(options[60])

    def _extract_from_vdi(self, vdi):
        # Vendor class identifier:
        #   "Cisco Systems, Inc." (Cisco 6901 9.1.2/9.2.1)
        #   "Cisco Systems, Inc. IP Phone 7912" (Cisco 7912 9.0.3)
        #   "Cisco Systems, Inc. IP Phone CP-7940G\x00" (Cisco 7940 8.1.2)
        #   "Cisco Systems, Inc. IP Phone CP-7941G\x00" (Cisco 7941 9.0.3)
        #   "Cisco Systems, Inc. IP Phone CP-7960G\x00" (Cisco 7960 8.1.2)
        #   "Cisco Systems, Inc. IP Phone CP-8961\x00" (Cisco 8961 9.1.2)
        #   "Cisco Systems, Inc. IP Phone CP-9951\x00" (Cisco 9951 9.1.2)
        #   "Cisco Systems Inc. Wireless Phone 7921"
        if vdi.startswith('Cisco Systems'):
            dev_info = {u'vendor':  u'Cisco'}
            m = self._VDI_REGEX.search(vdi)
            if m:
                _7900_modelnum = m.group(1) or m.group(2)
                if _7900_modelnum:
                    if _7900_modelnum == '20':
                        fmt = u'79%s'
                    else:
                        fmt = u'79%sG'
                    dev_info[u'model'] = fmt % _7900_modelnum
                else:
                    model_num = m.group(3)
                    dev_info[u'model'] = model_num.decode('ascii')
                    logger.debug('Model: %s', dev_info[u'model'])
            return dev_info


class BaseCiscoHTTPDeviceInfoExtractor(object):
    _CIPC_REGEX = re.compile(r'^/Communicator[/\\]')
    _FILENAME_REGEXES = [
        re.compile(r'^/SEP([\dA-F]{12})\.cnf\.xml$'),
        re.compile(r'^/CTLSEP([\dA-F]{12})\.tlv$'),
        re.compile(r'^/ITLSEP([\dA-F]{12})\.tlv$'),
        re.compile(r'^/ITLFile\.tlv$'),
    ]

    def extract(self, request, request_type):
        return defer.succeed(self._do_extract(request))

    def _do_extract(self, request):
        if self._CIPC_REGEX.match(request.path):
            return {u'vendor': u'Cisco', u'model': u'CIPC'}
        for regex in self._FILENAME_REGEXES:
            m = regex.match(request.path)
            if m:
                dev_info = {u'vendor': u'Cisco'}
                if m.lastindex == 1:
                    try:
                        dev_info[u'mac'] = norm_mac(m.group(1).decode('ascii'))
                    except ValueError, e:
                        logger.warning('Could not normalize MAC address: %s', e)
                return dev_info


class BaseCiscoTFTPDeviceInfoExtractor(object):
    _CIPC_REGEX = re.compile(r'^Communicator[/\\]')
    _FILENAME_REGEXES = [
        re.compile(r'^SEP([\dA-F]{12})\.cnf\.xml$'),
        re.compile(r'^CTLSEP([\dA-F]{12})\.tlv$'),
        re.compile(r'^ITLSEP([\dA-F]{12})\.tlv$'),
        re.compile(r'^ITLFile\.tlv$'),
    ]

    def extract(self, request, request_type):
        return defer.succeed(self._do_extract(request))

    def _do_extract(self, request):
        packet = request['packet']
        filename = packet['filename']
        if self._CIPC_REGEX.match(filename):
            return {u'vendor': u'Cisco', u'model': u'CIPC'}
        for regex in self._FILENAME_REGEXES:
            m = regex.match(filename)
            if m:
                dev_info = {u'vendor': u'Cisco'}
                return dev_info


_ZONE_MAP = {
    'Etc/GMT+12': u'Dateline Standard Time',
    'Pacific/Samoa': u'Samoa Standard Time ',
    'US/Hawaii': u'Hawaiian Standard Time ',
    'US/Alaska': u'Alaskan Standard/Daylight Time',
    'US/Pacific': u'Pacific Standard/Daylight Time',
    'US/Mountain': u'Mountain Standard/Daylight Time',
    'Etc/GMT+7': u'US Mountain Standard Time',
    'US/Central': u'Central Standard/Daylight Time',
    'America/Mexico_City': u'Mexico Standard/Daylight Time',
#    '': u'Canada Central Standard Time',
#    '': u'SA Pacific Standard Time',
    'US/Eastern': u'Eastern Standard/Daylight Time',
    'Etc/GMT+5': u'US Eastern Standard Time',
    'Canada/Atlantic': u'Atlantic Standard/Daylight Time',
    'Etc/GMT+4': u'SA Western Standard Time',
    'Canada/Newfoundland': u'Newfoundland Standard/Daylight Time',
    'America/Sao_Paulo': u'South America Standard/Daylight Time',
    'Etc/GMT+3': u'SA Eastern Standard Time',
    'Etc/GMT+2': u'Mid-Atlantic Standard/Daylight Time',
    'Atlantic/Azores': u'Azores Standard/Daylight Time',
    'Europe/London': u'GMT Standard/Daylight Time',
    'Etc/GMT': u'Greenwich Standard Time',
#    'Europe/Belfast': u'W. Europe Standard/Daylight Time',
#    '': u'GTB Standard/Daylight Time',
    'Egypt': u'Egypt Standard/Daylight Time',
    'Europe/Athens': u'E. Europe Standard/Daylight Time',
#    'Europe/Rome': u'Romance Standard/Daylight Time',
    'Europe/Paris': u'Central Europe Standard/Daylight Time',
    'Africa/Johannesburg': u'South Africa Standard Time ',
    'Asia/Jerusalem': u'Jerusalem Standard/Daylight Time',
    'Asia/Riyadh': u'Saudi Arabia Standard Time',
    'Europe/Moscow': u'Russian Standard/Daylight Time', # Russia covers 8 time zones.
    'Iran': u'Iran Standard/Daylight Time',
#    '': u'Caucasus Standard/Daylight Time',
    'Etc/GMT-4': u'Arabian Standard Time',
    'Asia/Kabul': u'Afghanistan Standard Time ',
    'Etc/GMT-5': u'West Asia Standard Time',
#    '': u'Ekaterinburg Standard Time',
    'Asia/Calcutta': u'India Standard Time',
    'Etc/GMT-6': u'Central Asia Standard Time ',
    'Etc/GMT-7': u'SE Asia Standard Time',
#    '': u'China Standard/Daylight Time', # China doesn't observe DST since 1991
    'Asia/Taipei': u'Taipei Standard Time',
    'Asia/Tokyo': u'Tokyo Standard Time',
    'Australia/ACT': u'Cen. Australia Standard/Daylight Time',
    'Australia/Brisbane': u'AUS Central Standard Time',
#    '': u'E. Australia Standard Time',
#    '': u'AUS Eastern Standard/Daylight Time',
    'Etc/GMT-10': u'West Pacific Standard Time',
    'Australia/Tasmania': u'Tasmania Standard/Daylight Time',
    'Etc/GMT-11': u'Central Pacific Standard Time',
    'Etc/GMT-12': u'Fiji Standard Time',
#    '': u'New Zealand Standard/Daylight Time',
}


def _gen_tz_map():
    result = {}
    for tz_name, param_value in _ZONE_MAP.iteritems():
        tzinfo = tzinform.get_timezone_info(tz_name)
        inner_dict = result.setdefault(tzinfo['utcoffset'].as_minutes, {})
        if not tzinfo['dst']:
            inner_dict[None] = param_value
        else:
            inner_dict[tzinfo['dst']['as_string']] = param_value
    return result


class BaseCiscoSipPlugin(StandardPlugin):
    # XXX actually, we didn't find which encoding Cisco Sip are using
    _ENCODING = 'UTF-8'
    _TZ_MAP = _gen_tz_map()
    _TZ_VALUE_DEF = u'Eastern Standard/Daylight Time'
    _LOCALE = {
        # <locale>: (<name>, <lang code>, <network locale>)
        u'de_DE': (u'german_germany', u'de', u'germany'),
        u'en_US': (u'english_united_states', u'en', u'united_states'),
        u'es_ES': (u'spanish_spain', u'es', u'spain'),
        u'fr_FR': (u'french_france', u'fr', u'france'),
        u'fr_CA': (u'french_france', u'fr', u'canada')
    }

    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)

        self._tpl_helper = TemplatePluginHelper(plugin_dir)

        downloaders = FetchfwPluginHelper.new_downloaders(gen_cfg.get('proxies'))
        fetchfw_helper = FetchfwPluginHelper(plugin_dir, downloaders)

        self.services = fetchfw_helper.services()

        # Maybe find a way to bind to a specific port without changing the general http_port setting of xivo-provd ?
        # At the moment, http_port 6970 must be set in /etc/xivo/provd/provd.conf
        self.http_service = HTTPNoListingFileService(self._tftpboot_dir)
        
        self.tftp_service = TFTPFileService(self._tftpboot_dir)

    dhcp_dev_info_extractor = BaseCiscoDHCPDeviceInfoExtractor()

    http_dev_info_extractor = BaseCiscoHTTPDeviceInfoExtractor()

    tftp_dev_info_extractor = BaseCiscoTFTPDeviceInfoExtractor()

    def _add_locale(self, raw_config):
        locale = raw_config.get(u'locale')
        logger.debug('locale in raw_config: %s', locale)
        if locale in self._LOCALE:
            raw_config[u'XX_locale'] = self._LOCALE[locale]

    def _tzinfo_to_value(self, tzinfo):
        utcoffset_m = tzinfo['utcoffset'].as_minutes
        if utcoffset_m not in self._TZ_MAP:
            # No UTC offset matching. Let's try finding one relatively close...
            for supp_offset in [30, -30, 60, -60]:
                if utcoffset_m + supp_offset in self._TZ_MAP:
                    utcoffset_m += supp_offset
                    break
            else:
                return self._TZ_VALUE_DEF

        dst_map = self._TZ_MAP[utcoffset_m]
        if tzinfo['dst']:
            dst_key = tzinfo['dst']['as_string']
        else:
            dst_key = None
        if dst_key not in dst_map:
            # No DST rules matching. Fallback on all-standard time or random
            # DST rule in last resort...
            if None in dst_map:
                dst_key = None
            else:
                dst_key = dst_map.keys()[0]
        return dst_map[dst_key]

    def _add_timezone(self, raw_config):
        raw_config[u'XX_timezone'] = self._TZ_VALUE_DEF
        if u'timezone' in raw_config:
            try:
                tzinfo = tzinform.get_timezone_info(raw_config[u'timezone'])
            except tzinform.TimezoneNotFoundError, e:
                logger.info('Unknown timezone: %s', e)
            else:
                raw_config[u'XX_timezone'] = self._tzinfo_to_value(tzinfo)

    def _add_xivo_phonebook_url(self, raw_config):
        if hasattr(plugins, 'add_xivo_phonebook_url') and raw_config.get(u'config_version', 0) >= 1:
            plugins.add_xivo_phonebook_url(raw_config, u'cisco', entry_point=u'menu')
        else:
            self._add_xivo_phonebook_url_compat(raw_config)

    def _add_xivo_phonebook_url_compat(self, raw_config):
        hostname = raw_config.get(u'X_xivo_phonebook_ip')
        if hostname:
            raw_config[u'XX_xivo_phonebook_url'] = u'http://{hostname}/service/ipbx/web_services.php/phonebook/menu/'.format(hostname=hostname)

    def _update_call_managers(self, raw_config):
        for priority, call_manager in raw_config[u'sccp_call_managers'].iteritems():
            call_manager[u'XX_priority'] = unicode(int(priority) - 1)

    def _update_sip_lines(self, raw_config):
        assert raw_config[u'sip_lines']
        sip_lines_key = min(raw_config[u'sip_lines'])
        sip_line = raw_config[u'sip_lines'][sip_lines_key]
        proxy_port = raw_config.get(u'sip_proxy_port', u'5060')
        voicemail = raw_config.get(u'exten_voicemail')
        for line in raw_config[u'sip_lines'].itervalues():
            line.setdefault(u'proxy_port', proxy_port)
            if voicemail:
                line.setdefault(u'voicemail', voicemail)
        def set_if(line_id, id):
            if line_id in sip_line:
                raw_config[id] = sip_line[line_id]
        set_if(u'proxy_ip', u'sip_proxy_ip')
        set_if(u'proxy_port', u'sip_proxy_port')
        set_if(u'backup_proxy_ip', u'sip_backup_proxy_ip')
        set_if(u'backup_proxy_port', u'sip_backup_proxy_port')
        set_if(u'outbound_proxy_ip', u'sip_outbound_proxy_ip')
        set_if(u'outbound_proxy_port', u'sip_outbound_proxy_port')
        set_if(u'registrar_ip', u'sip_registrar_ip')
        set_if(u'registrar_port', u'sip_registrar_port')
        set_if(u'backup_registrar_ip', u'sip_backup_registrar_ip')
        set_if(u'backup_registrar_port', u'sip_backup_registrar_port')

    def _add_fkeys(self, raw_config):
        assert raw_config[u'sip_lines']
        logger.debug('Func keys: %s', raw_config[u'funckeys'])

        if raw_config[u'funckeys']:
            fkeys_lines = [int(line) for line in raw_config[u'sip_lines']]
            fkeys_start = max(fkeys_lines)

            fkeys = {}
            fkey_type = {
                u'blf': 21,
                u'speeddial': 2,
                }
            
            for line_no, line_info in raw_config[u'funckeys'].iteritems():
                line_id = str(fkeys_start + int(line_no))
                fkeys[line_id] = raw_config[u'funckeys'][line_no]
                fkeys[line_id][u'feature_id'] = fkey_type[line_info[u'type']]
            
            raw_config[u'XX_fkeys'] = fkeys
    
    _SENSITIVE_FILENAME_REGEX = re.compile(r'^SEP[0-9A-F]{12}\.cnf\.xml$')

    def _dev_specific_filename(self, device):
        # Return the device specific filename (not pathname) of device
        fmted_mac = format_mac(device[u'mac'], separator='', uppercase=True)
        return 'SEP%s.cnf.xml' % fmted_mac

    def _check_config(self, raw_config):
        if u'tftp_port' not in raw_config:
            raise RawConfigError('only support configuration via TFTP')

    def _check_device(self, device):
        if u'mac' not in device:
            raise Exception('MAC address needed for device configuration')

    def configure(self, device, raw_config):
        self._check_config(raw_config)
        self._check_device(device)
        filename = self._dev_specific_filename(device)
        tpl = self._tpl_helper.get_dev_template(filename, device)

        # TODO check support for addons, and test what the addOnModules is
        #      really doing...
        raw_config[u'XX_addons'] = ''
        raw_config[u'protocol'] = 'SIP'
        self._add_locale(raw_config)
        self._add_timezone(raw_config)
        self._add_xivo_phonebook_url(raw_config)
        self._update_call_managers(raw_config)
        self._update_sip_lines(raw_config)
        self._add_fkeys(raw_config)

        path = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, raw_config, path, self._ENCODING)

    def deconfigure(self, device):
        path = os.path.join(self._tftpboot_dir, self._dev_specific_filename(device))
        try:
            os.remove(path)
        except OSError, e:
            # ignore
            logger.info('error while removing file: %s', e)

    def synchronize(self, device, raw_config):
        try:
            action = [
                'Content-type=text/plain',
                'Content=action=restart', # restart unregisters and redownloads config files from the server, reset unregisters and reboots the phone
                'Content=RegisterCallId={}',
                'Content=ConfigVersionStamp={0000000000000000}',
                'Content=DialplanVersionStamp={0000000000000000}',
                'Content=SoftkeyVersionStamp={0000000000000000}',
            ]
            return synchronize.standard_sip_synchronize(device, event='service-control', extra_vars=action)
        except TypeError: # xivo-provd not up to date for extra_vars
            return defer.fail(Exception('operation not supported, please update your xivo-provd'))

    def is_sensitive_filename(self, filename):
        return bool(self._SENSITIVE_FILENAME_REGEX.match(filename))
