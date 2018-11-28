# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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

import os

common_globals = {}
execfile_('common.py', common_globals)

MODEL_VERSIONS = {
    u'T19P_E2': u'53.80.0.95',
    u'T21P_E2': u'52.80.0.95',
    u'T23P': u'44.80.0.95',
    u'T23G': u'44.80.0.95',
    u'T27P': u'45.80.0.95',
    u'T29G': u'46.80.0.95',
    u'T40P': u'54.80.0.95',
    u'T41P': u'36.80.0.95',
    u'T42G': u'29.80.0.95',
    u'T46G': u'28.80.0.95',
    u'T48G': u'35.80.0.95',
    u'T49G': u'51.80.0.100',
    u'CP860': u'37.80.0.30',
    u'CP960': u'73.80.0.35',
    u'W52P': u'25.80.0.15',
}
COMMON_FILES = [
    ('y000000000028.cfg', u'T46-28.80.0.95.rom', 'model.tpl'),
    ('y000000000029.cfg', u'T42-29.80.0.95.rom', 'model.tpl'),
    ('y000000000035.cfg', u'T48-35.80.0.95.rom', 'model.tpl'),
    ('y000000000036.cfg', u'T41-36.80.0.95.rom', 'model.tpl'),
    ('y000000000044.cfg', u'T23-44.80.0.95.rom', 'model.tpl'),
    ('y000000000045.cfg', u'T27-45.80.0.95.rom', 'model.tpl'),
    ('y000000000046.cfg', u'T29-46.80.0.95.rom', 'model.tpl'),
    ('y000000000051.cfg', u'T49-51.80.0.100.rom', 'model.tpl'),
    ('y000000000052.cfg', u'T21P_E2-52.80.0.95.rom', 'model.tpl'),
    ('y000000000053.cfg', u'T19P_E2-53.80.0.95.rom', 'model.tpl'),
    ('y000000000054.cfg', u'T40-54.80.0.95.rom', 'model.tpl'),
    ('y000000000037.cfg', u'CP860-37.80.0.30.rom', 'model.tpl'),
    ('y000000000073.cfg', u'CP960-73.80.0.35.rom', 'model.tpl'),
]

COMMON_FILES_DECT = [
    ('y000000000025.cfg', u'Base for W52P&W56P-25.80.0.15.rom', u'W56H-61.80.0.15.rom', 'W52P.tpl'),
]


class YealinkPlugin(common_globals['BaseYealinkPlugin']):
    IS_PLUGIN = True

    pg_associator = common_globals['BaseYealinkPgAssociator'](MODEL_VERSIONS)

    # Yealink plugin specific stuff

    _COMMON_FILES = COMMON_FILES

    def configure_common(self, raw_config):
        super(YealinkPlugin, self).configure_common(raw_config)
        for filename, fw_filename, fw_handset_filename, tpl_filename in COMMON_FILES_DECT:
            tpl = self._tpl_helper.get_template('common/%s' % tpl_filename)
            dst = os.path.join(self._tftpboot_dir, filename)
            raw_config[u'XX_fw_filename'] = fw_filename
            raw_config[u'XX_fw_handset_filename'] = fw_handset_filename
            self._tpl_helper.dump(tpl, raw_config, dst, self._ENCODING)
