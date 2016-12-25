# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import TokenHandler,SingleStandardHanler,MultiStandardHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

logger = get_logger("debug")

class AreaListHandler(MultiStandardHandler,TokenHandler):
    _model = "area.AreaModel"

class AreaHandler(SingleStandardHanler,TokenHandler):
    _model = "area.AreaMode"


handlers = [
            (r"", AreaListHandler,get_provider('frontend')),
            (r"/(.*)", AreaHandler,get_provider('frontend')),
            ]
