# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict

    from ..common.common import BaseGigasetPgAssociator, BaseGigasetPlugin  # noqa: F401

    class CommonGlobalsDict(TypedDict):
        BaseGigasetPlugin: type[BaseGigasetPlugin]
        BaseGigasetPgAssociator: type[BaseGigasetPgAssociator]


common: CommonGlobalsDict = {}  # type: ignore[typeddict-item]
execfile_('common.py', common)  # type: ignore[name-defined]


MODEL_VERSIONS = {
    'N720 DM PRO': '70.117.00.000.000',
    'N720 IP PRO': '70.117.00.000.000',
}


class GigasetPlugin(common['BaseGigasetPlugin']):  # type: ignore[valid-type,misc]
    IS_PLUGIN = True

    pg_associator = common['BaseGigasetPgAssociator'](MODEL_VERSIONS)
