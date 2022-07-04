# -*- coding: utf-8 -*-

# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

common_globals = {}
execfile_('common.py', common_globals)

MODEL_VERSIONS = {
    u'T19P_E2': u'53.83.0.35',
    u'T21P_E2': u'52.83.0.35',
    u'T23P': u'44.83.0.35',
    u'T23G': u'44.83.0.35',
    u'T27P': u'45.83.0.35',
    u'T27G': u'69.83.0.35',
    u'T29G': u'46.83.0.35',
    u'T40P': u'54.83.0.35',
    u'T40G': u'76.83.0.35',
    u'CP960': u'73.83.0.30',
    u'T29G': u'46.83.0.120',
    u'T41P': u'36.83.0.35',
    u'T41S': u'66.83.0.35',
    u'T42G': u'29.83.0.35',
    u'T42S': u'66.83.0.35',
    u'T46G': u'28.83.0.35',
    u'T46S': u'66.83.0.35',
    u'T48G': u'35.83.0.35',
    u'T48S': u'66.83.0.35',
    u'T52S': u'70.83.0.35',
    u'T54S': u'70.83.0.35',
    u'T56A': u'58.83.0.5',
    u'T58': u'58.83.0.5',
    u'T42G': u'29.83.0.120',
    u'T46G': u'28.83.0.120',
    u'T48G': u'35.83.0.120',
    u'T56A': u'58.83.0.15',
    u'T58': u'58.83.0.15',
    u'W60B': u'77.83.0.85',
    u'W80B': u'103.83.0.122',
    u'W80DM': u'103.83.0.122',
}

COMMON_FILES = [
    ('y000000000044.cfg', u'T23-44.83.0.35.rom', 'model.tpl'),
    ('y000000000045.cfg', u'T27-45.83.0.35.rom', 'model.tpl'),
    ('y000000000069.cfg', u'T27G-69.83.0.35.rom', 'model.tpl'),
    ('y000000000052.cfg', u'T21P_E2-52.83.0.35.rom', 'model.tpl'),
    ('y000000000053.cfg', u'T19P_E2-53.83.0.35.rom', 'model.tpl'),
    ('y000000000054.cfg', u'T40-54.83.0.35.rom', 'model.tpl'),
    ('y000000000076.cfg', u'T40G-76.83.0.35.rom', 'model.tpl'),
    ('y000000000066.cfg', u'T46S(T48S,T42S,T41S)-66.83.0.35.rom', 'model.tpl'),
    ('y000000000068.cfg', u'T46S(T48S,T42S,T41S)-66.83.0.35.rom', 'model.tpl'),
    ('y000000000070.cfg', u'T54S(T52S)-70.83.0.35.rom', 'model.tpl'),
    ('y000000000028.cfg', u'T46-28.83.0.120.rom', 'model.tpl'),
    ('y000000000029.cfg', u'T42-29.83.0.120.rom', 'model.tpl'),
    ('y000000000035.cfg', u'T48-35.83.0.120.rom', 'model.tpl'),
    ('y000000000036.cfg', u'T41-36.83.0.120.rom', 'model.tpl'),
    ('y000000000046.cfg', u'T29-46.83.0.120.rom', 'model.tpl'),
    ('y000000000058.cfg', u'T58V(T56A)-58.83.0.15.rom', 'model.tpl'),
    ('y000000000073.cfg', u'CP960-73.83.0.30.rom', 'model.tpl'),
]

HANDSETS_FW = {
    'w53h': u'W53H-88.83.0.90.rom',
    'w56h': u'W56H-61.83.0.90.rom',
    'w59r': u'W59R-115.83.0.10.rom',
    'cp930w': u'CP930W-87.83.0.60.rom',
}

COMMON_FILES_DECT = [
    {
        'filename': u'y000000000077.cfg',
        'fw_filename': u'W60B-77.83.0.85.rom',
        'handsets_fw': HANDSETS_FW,
        'tpl_filename': u'dect_model.tpl',
    },
    {
        'filename': u'y000000000103.cfg',
        'fw_filename': u'$PN-103.83.0.122.rom',  # $PN = Product Name, i.e W80B
        'handsets_fw': HANDSETS_FW,
        'tpl_filename': u'dect_model.tpl',
    }
]


class YealinkPlugin(common_globals['BaseYealinkPlugin']):
    IS_PLUGIN = True

    pg_associator = common_globals['BaseYealinkPgAssociator'](MODEL_VERSIONS)

    # Yealink plugin specific stuff

    _COMMON_FILES = COMMON_FILES

    def configure_common(self, raw_config):
        super(YealinkPlugin, self).configure_common(raw_config)
        for dect_info in COMMON_FILES_DECT:
            tpl = self._tpl_helper.get_template('common/%s' % dect_info[u'tpl_filename'])
            dst = os.path.join(self._tftpboot_dir, dect_info[u'filename'])
            raw_config[u'XX_handsets_fw'] = dect_info[u'handsets_fw']
            raw_config[u'XX_fw_filename'] = dect_info[u'fw_filename']

            self._tpl_helper.dump(tpl, raw_config, dst, self._ENCODING)
