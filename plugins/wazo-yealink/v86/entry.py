# -*- coding: utf-8 -*-

# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

common_globals = {}
execfile_('common.py', common_globals)

MODEL_VERSIONS = {
    u'CP920': u'78.86.0.15',
    u'T27G': u'69.86.0.15',
    u'T30': u'124.86.0.20',
    u'T30P': u'124.86.0.20',
    u'T31': u'124.86.0.20',
    u'T31P': u'124.86.0.20',
    u'T31G': u'124.86.0.20',
    u'T33': u'124.86.0.20',
    u'T33P': u'124.86.0.20',
    u'T33G': u'124.86.0.20',
    u'T41S': u'66.86.0.15',
    u'T42S': u'66.86.0.15',
    u'T46S': u'66.86.0.15',
    u'T48S': u'66.86.0.15',
    u'T41U': u'108.86.0.45',
    u'T42U': u'108.86.0.45',
    u'T43U': u'108.86.0.45',
    u'T46U': u'108.86.0.45',
    u'T48U': u'108.86.0.45',
    u'T53': u'96.86.0.45',
    u'T53C': u'96.86.0.45',
    u'T53W': u'96.86.0.45',
    u'T54W': u'96.86.0.45',
    u'T57': u'96.86.0.45',
    u'T57W': u'96.86.0.45',
    u'T56': u'58.86.0.20',
    u'T58': u'58.86.0.20',
    u'T58W': u'150.86.0.11',
}

COMMON_FILES = [
    ('y000000000069.cfg', u'T27G-69.86.0.15.rom', 'model.tpl'),
    ('y000000000065.cfg', u'T46S(T48S,T42S,T41S)-66.86.0.15.rom', 'model.tpl'),
    ('y000000000066.cfg', u'T46S(T48S,T42S,T41S)-66.86.0.15.rom', 'model.tpl'),
    ('y000000000067.cfg', u'T46S(T48S,T42S,T41S)-66.86.0.15.rom', 'model.tpl'),
    ('y000000000068.cfg', u'T46S(T48S,T42S,T41S)-66.86.0.15.rom', 'model.tpl'),
    ('y000000000108.cfg', u'T46U(T43U,T46U,T41U,T48U,T42U)-108.86.0.45(20211130).rom', 'model.tpl'),
    ('y000000000123.cfg', u'T31(T30,T30P,T31G,T31P,T33P,T33G)-124.86.0.40.rom', 'model.tpl'),
    ('y000000000124.cfg', u'T31(T30,T30P,T31G,T31P,T33P,T33G)-124.86.0.40.rom', 'model.tpl'),
    ('y000000000127.cfg', u'T31(T30,T30P,T31G,T31P,T33P,T33G)-124.86.0.40.rom', 'model.tpl'),
    ('y000000000150.cfg', u'T58W-150.86.0.11.rom', 'model.tpl'),
]

HANDSETS_FW = {
    'w53h': u'W53H-88.85.0.20.rom',
    'w56h': u'W56H-61.85.0.20.rom',
    'w59r': u'W59R-115.85.0.20.rom',
    'cp930w': u'CP930W-87.85.0.20.rom',
    't41s_dd10k': u'T4S-ddphone-66.85.0.56.rom',
    't54w_dd10k': u'T54W-ddphone-96.85.0.65.rom ',
}

COMMON_FILES_DECT = [
    {
        'filename': u'y000000000058.cfg',
        'fw_filename': u'T58V(T56A)-58.86.0.20.rom',
        'handsets_fw': HANDSETS_FW,
        'tpl_filename': u'dect_model.tpl',
    },
    {
        'filename': u'y000000000095.cfg',
        'fw_filename': u'T54W(T57W,T53W,T53,T53C,T54,T57)-96.86.0.45(20211130).rom',
        'handsets_fw': HANDSETS_FW,
        'tpl_filename': u'dect_model.tpl',
    },
    {
        'filename': u'y000000000096.cfg',
        'fw_filename': u'T54W(T57W,T53W,T53,T53C,T54,T57)-96.86.0.45(20211130).rom',
        'handsets_fw': HANDSETS_FW,
        'tpl_filename': u'dect_model.tpl',
    },
    {
        'filename': u'y000000000097.cfg',
        'fw_filename': u'T54W(T57W,T53W,T53,T53C,T54,T57)-96.86.0.45(20211130).rom',
        'handsets_fw': HANDSETS_FW,
        'tpl_filename': u'dect_model.tpl',
    },
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
