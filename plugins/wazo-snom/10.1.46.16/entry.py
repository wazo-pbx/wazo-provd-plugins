# -*- coding: utf-8 -*-

# Copyright 2018 The Wazo Authors  (see AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

common_globals = {}
execfile_('common.py', common_globals)

MODELS = [
	u'D375',
    u'D385',
	u'715',
	u'D717',
	u'725',
	u'D735',
	u'D745',
	u'D765',
	u'D785',
]
VERSION = u'10.1.46.16'


class SnomPlugin(common_globals['BaseSnomPlugin']):
    IS_PLUGIN = True

    _MODELS = MODELS

    pg_associator = common_globals['BaseSnomPgAssociator'](MODELS, VERSION)
