# Copyright 2010-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict

    from ..common.common import (  # noqa: F401
        BaseFanvilHTTPDeviceInfoExtractor,
        BaseFanvilPgAssociator,
        BaseFanvilPlugin,
    )

    class CommonGlobalsDict(TypedDict):
        BaseFanvilPlugin: type[BaseFanvilPlugin]
        BaseFanvilPgAssociator: type[BaseFanvilPgAssociator]
        BaseFanvilHTTPDeviceInfoExtractor: type[BaseFanvilHTTPDeviceInfoExtractor]


common: CommonGlobalsDict = {}  # type: ignore[typeddict-item]
execfile_('common.py', common)  # type: ignore[name-defined]

MODELS = [
    'V61G',
    'V61W',
    'V62',
    'V62G',
    'V62W',
    'V62Pro',
    'V63',
    'V64',
    'V65',
    'V66',
    'V66Pro',
    'V67',
]

MODEL_FIRMWARE_MAPPING = {
    'V61G': 'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
    'V61W': 'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
    'V62': 'v62-fanvil-release-ff01-5944-2.12.20-krnlvUT2024-07-16-04.36.28.z',
    'V62G': 'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
    'V62W': 'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
    'V62Pro': 'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
    'V63': 'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
    'V64': 'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
    'V65': 'v65-fanvil-release-5924-2.12.21.1-krnvlT2024-08-28-09.41.46.z',
    'V66': 'v66pro-fanvil-release-5927-2.12.18.16-krnvlT2024-12-13-19.26.56.z',
    'V66Pro': 'v66pro-fanvil-release-5927-2.12.18.16-krnvlT2024-12-13-19.26.56.z',
    'V67': 'v67_fanvil_2.6.10.1992_20241023_full.zip',
}

COMMON_FILES = {
    'F0V0V6700000.cfg': (
        'V67',
        'v67_fanvil_2.6.10.1992_20241023_full.zip',
        'model-v.tpl',
    ),
    'fanvil_v67_hw1_1.txt': (
        'V67',
        'v67_fanvil_2.6.10.1992_20241023_full.zip',
        'model-v67.tpl',
    ),
    'F0VV61G00000.cfg': (
        'V61G',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v.tpl',
    ),
    'fanvil_v61g_hwv1_0.txt': (
        'V61G',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v6x.tpl',
    ),
    'F0VV61W00000.cfg': (
        'V61W',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v.tpl',
    ),
    'fanvil_v61w_hwv1_0.txt': (
        'V61W',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v6x.tpl',
    ),
    'F0VV6200000.cfg': (
        'V62',
        'v62-fanvil-release-ff01-5944-2.12.20-krnlvUT2024-07-16-04.36.28.z',
        'model-v.tpl',
    ),
    'fanvil_v62_hwv1_0.txt': (
        'V62',
        'v62-fanvil-release-ff01-5944-2.12.20-krnlvUT2024-07-16-04.36.28.z',
        'model-v6x.tpl',
    ),
    'F0V0V6210000.cfg': (
        'V62Pro',
        'v62-fanvil-release-ff01-5944-2.12.20-krnlvUT2024-07-16-04.36.28.z',
        'model-v.tpl',
    ),
    'fanvil_v62_pro_hwv1_0.txt': (
        'V62Pro',
        'v62-fanvil-release-ff01-5944-2.12.20-krnlvUT2024-07-16-04.36.28.z',
        'model-v6x.tpl',
    ),
    'F0VV62G00000.cfg': (
        'V62G',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v.tpl',
    ),
    'fanvil_v62g_hwv1_0.txt': (
        'V62G',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v6x.tpl',
    ),
    'F0VV62W00000.cfg': (
        'V62W',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v.tpl',
    ),
    'fanvil_v62w_hwv1_0.txt': (
        'V62',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v6x.tpl',
    ),
    'F0V0V6300000.cfg': (
        'V63',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v.tpl',
    ),
    'fanvil_v63_hwv1_0.txt': (
        'V63',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v6x.tpl',
    ),
    'F0V0V6400000.cfg': (
        'V64',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v.tpl',
    ),
    'fanvil_v64_hwv1_0.txt': (
        'V64',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v6x.tpl',
    ),
    'F0V0V6500000.cfg': (
        'V65',
        'v65-fanvil-release-5924-2.12.21.1-krnvlT2024-08-28-09.41.46.z',
        'model-v.tpl',
    ),
    'fanvil_v65_hwv1_0.txt': (
        'V65',
        'v65-fanvil-release-5924-2.12.21.1-krnvlT2024-08-28-09.41.46.z',
        'model-v65.tpl',
    ),
    'F0V0V6600000.cfg': (
        'V66',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v.tpl',
    ),
    'fanvil_v66_hwv1_0.txt': (
        'V66',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v66.tpl',
    ),
    'F0V0V66100000.cfg': (
        'V66Pro',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v.tpl',
    ),
    'fanvil_v66_pro_hwv1_0.txt': (
        'V66Pro',
        'v6x-unified-release-a006-2.12.20.3-krvnlUT2024-12-12-16.09.35.z',
        'model-v66.tpl',
    ),
}

FUNCTION_KEYS_PER_PAGE = {
    'V67': 29,
    'V66': 29,
    'V66Pro': 29,
    'V65': 9,
    'V64': 7,
    'V63': 7,
    'V62': 5,
    'V62G': 7,
    'V62W': 7,
    'V62Pro': 7,
    'V61G': 4,
    'V61W': 4,
}


class FanvilPlugin(common['BaseFanvilPlugin']):  # type: ignore[valid-type,misc]
    IS_PLUGIN = True

    _COMMON_FILES = COMMON_FILES
    _MODEL_FIRMWARE_MAPPING = MODEL_FIRMWARE_MAPPING
    _FUNCTION_KEYS_PER_PAGE = FUNCTION_KEYS_PER_PAGE
    _TOP_FUNCTION_KEYS: dict[str, int] = {}
    _LINE_KEYS_PER_PAGE: dict[str, int] = {}
    _LOCALE = {
        'de_DE': '16',
        'es_ES': '6',
        'fr_FR': '5',
        'fr_CA': '5',
        'it_IT': '7',
        'nl_NL': '3',
        'en_US': '0',
    }
    _TZ_INFO = {
        -12: [('UTC-12', -48)],
        -11: [('UTC-11', -44)],
        -10: [('UTC-10', -40)],
        -9: [('UTC-09', -36)],
        -8: [('UTC-08', -32)],
        -7: [('UTC-07', -28)],
        -6: [('UTC-06', -24)],
        -5: [('UTC-05', -20)],
        -4: [('UTC-04', -16)],
        -3: [('UTC-03', -12)],
        -2: [('UTC-02', -8)],
        -1: [('UTC-01', -4)],
        0: [('UCT', 0)],
        1: [('UTC+1', 4)],
        2: [('UTC+2', 8)],
        3: [('UTC+3', 12)],
        4: [('UTC+4', 16)],
        5: [('UTC+5', 20)],
        6: [('UTC+6', 24)],
        7: [('UTC+7', 28)],
        8: [('UTC+8', 32)],
        9: [('UTC+9', 36)],
        10: [('UTC+10', 40)],
        11: [('UTC+11', 44)],
        12: [('UTC+12', 48)],
    }

    pg_associator = common['BaseFanvilPgAssociator'](MODELS)
    http_dev_info_extractor = common['BaseFanvilHTTPDeviceInfoExtractor'](_COMMON_FILES)
