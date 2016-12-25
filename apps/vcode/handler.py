# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import TokenHandler,SingleStandardHanler,MultiStandardHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

logger = get_logger("debug")

class VcodeListHandler(MultiStandardHandler):
    _model = "vcode.VcodeModel"

class VcodeHandler(SingleStandardHanler,TokenHandler):
    _model = "vcode.VcodeModel"

class VcodeVerifyHandler(MultiStandardHandler):
    _model = "vcode.VcodeModel"

    def _put(self):
        self.result['data'] = self.model.validate_code()

handlers = [
            (r"", VcodeListHandler),
            (r"/verify", VcodeVerifyHandler),
            (r"/(.*)", VcodeHandler,get_provider('backend')),
            ]
