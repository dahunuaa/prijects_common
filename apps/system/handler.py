# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import TokenHandler, SingleStandardHanler, MultiStandardHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

logger = get_logger("debug")


class SystemListHandler(MultiStandardHandler, TokenHandler):
    _model = "system.SystemModel"

    def _post(self):
        if self.user_id is not None:
            self.model.set_argument("user_id",self.user_id)
        super(SystemListHandler, self)._post()


class SystemHandler(SingleStandardHanler, TokenHandler):
    _model = "system.SystemModel"


handlers = [
    (r"", SystemListHandler, get_provider('frontend')),
    (r"/(.*)", SystemHandler, get_provider('frontend')),
]
