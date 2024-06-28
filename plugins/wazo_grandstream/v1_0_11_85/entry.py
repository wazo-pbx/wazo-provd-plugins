# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict

    from ..common.common import (  # noqa: F401
        BaseGrandstreamPgAssociator,
        BaseGrandstreamPlugin,
    )

    class CommonGlobalsDict(TypedDict):
        BaseGrandstreamPlugin: type[BaseGrandstreamPlugin]
        BaseGrandstreamPgAssociator: type[BaseGrandstreamPgAssociator]


common: CommonGlobalsDict = {}  # type: ignore[typeddict-item]
execfile_('common.py', common)  # type: ignore[name-defined]

MODELS = [
    'GXP2130',
    'GXP2135',
    'GXP2140',
    'GXP2150',
    'GXP2160',
]
VERSION = '1.0.11.85'


class GrandstreamPlugin(common['BaseGrandstreamPlugin']):  # type: ignore[valid-type,misc]
    IS_PLUGIN = True

    _MODELS = MODELS

    pg_associator = common['BaseGrandstreamPgAssociator'](MODELS, VERSION)
