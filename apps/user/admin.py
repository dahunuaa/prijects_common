# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import APIHandler,TokenHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

logger = get_logger("debug")

class AdminUserListHandler(TokenHandler,APIHandler):
    pass

class AdminUserHandler(TokenHandler,APIHandler):
    _model = "user.UserModel"

    #获取用户信息
    def get(self, *args, **kwargs):
        pass

    #用户登录
    def post(self, *args, **kwargs):
        try:
            pass
        except Exception as e:
            self.set_result(0, unicode(e))
        finally:
            logger.debug(self.request, self.result)

        self.finish(self.result)

    #修改用户
    def put(self, *args, **kwargs):
        pass


handlers = [
            (r"/", AdminUserListHandler,get_provider('backend')),#用户列表
            (r"/(.*)", AdminUserHandler,get_provider('backend')),#用户操作
            ]
