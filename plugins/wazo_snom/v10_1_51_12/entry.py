# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict

    from ..common.common import BaseSnomPgAssociator, BaseSnomPlugin  # noqa: F401

    class CommonGlobalsDict(TypedDict):
        BaseSnomPlugin: type[BaseSnomPlugin]
        BaseSnomPgAssociator: type[BaseSnomPgAssociator]


common_globals: CommonGlobalsDict = {}  # type: ignore[typeddict-item]
execfile_('common.py', common_globals)  # type: ignore[name-defined]

MODELS = [
    'D120',
    'D305',
    'D315',
    'D335',
    'D345',
    'D375',
    'D385',
    'D712',
    '715',
    'D717',
    '725',
    'D735',
    'D745',
    'D765',
    'D785',
]
VERSION = '10.1.51.12'


class SnomPlugin(common_globals['BaseSnomPlugin']):  # type: ignore[valid-type,misc]
    IS_PLUGIN = True

    _MODELS = MODELS

    pg_associator = common_globals['BaseSnomPgAssociator'](MODELS, VERSION)
