# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import TokenHandler, SingleStandardHanler, MultiStandardHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

logger = get_logger("debug")


class IconListHandler(MultiStandardHandler, TokenHandler):
    _model = "icon.IconModel"


class IconHandler(SingleStandardHanler, TokenHandler):
    _model = "icon.IconModel"


handlers = [
    (r"", IconListHandler, get_provider('frontend')),
    (r"/(.*)", IconHandler, get_provider('frontend')),
]
