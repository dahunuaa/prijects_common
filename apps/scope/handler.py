# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import TokenHandler, SingleStandardHanler, MultiStandardHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

logger = get_logger("debug")


class ScopeListHandler(MultiStandardHandler, TokenHandler):
    _model = "scope.ScopeModel"


class ScopeHandler(SingleStandardHanler, TokenHandler):
    _model = "scope.ScopeModel"


handlers = [
    (r"", ScopeListHandler, get_provider('admin')),
    (r"/(.*)", ScopeHandler, get_provider('admin')),
]
