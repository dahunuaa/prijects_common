# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import APIHandler, TokenHandler,SingleStandardHanler,MultiStandardHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

logger = get_logger("debug")


class UserListHandler(TokenHandler, MultiStandardHandler):
    _model = "user.UserModel"

class UserHandler(TokenHandler, SingleStandardHanler):
    _model = "user.UserModel"

class UserRegisterHandler(APIHandler):
    _model = "user.UserModel"

    # 注册用户
    def post(self, *args, **kwargs):
        '''

        :param args: mobile,password,login_name,permission,inviter_id,name,id_card,system,email
        :param kwargs:
        :return:
        '''
        try:
            self.model.set_request(self.request)
            res = self.model.new()

            self.result['data'] = res
        except Exception as e:
            self.set_result(0, str(e))
        finally:
            logger.debug(self.request, self.result)

        self.finish(self.result)


class UserLoginHandler(APIHandler):
    _model = "user.UserModel"

    # 用户登录
    def post(self, *args, **kwargs):
        try:
            mobile = self.get_argument("mobile", None)
            password = self.get_argument("password", None)
            scope = self.get_argument("scope", None)
            if mobile is None or password is None:
                raise ValueError(u"手机号或者密码为空")
            res = self.model.login(mobile, password, scope)
            self.result['data'] = res
        except Exception as e:
            self.set_result(0, str(e))
        finally:
            logger.debug(self.request, self.result)
        self.finish(self.result)


class UserLoginWexinHandler(APIHandler):
    _model = "user.UserModel"

    # 用户登录
    def post(self, *args, **kwargs):
        try:
            code = self.get_argument("code", None)
            if code is None:
                raise ValueError(u"微信授权码为空")
            self.model.set_request(self.request)
            res = self.model.new()
            self.result['data'] = res
        except Exception as e:
            self.set_result(0, str(e))
        finally:
            logger.debug(self.request, self.result)
        self.finish(self.result)


class UserPasswordResetHandler(TokenHandler, APIHandler):
    _model = "user.UserModel"

    # 修改密码
    def post(self, *args, **kwargs):
        try:
            mobile = self.get_argument("mobile", None)
            newpassword = self.get_argument("newpassword", None)
            scope = self.get_argument("scope", None)
            if mobile is None or newpassword is None:
                raise ValueError(u"手机号或者密码为空")
            res = self.model.changepwd(mobile, newpassword, scope)
            self.result['data'] = res
        except Exception as e:
            self.set_result(0, str(e))
        finally:
            logger.debug(self.request, self.result)
        self.finish(self.result)


handlers = [
    (r"/register", UserRegisterHandler),  # 用户注册
    (r"/login", UserLoginHandler),  # 用户登录
    (r"/login/weixin", UserLoginWexinHandler),  # 微信登录
    (r"/password/reset", UserPasswordResetHandler, get_provider('backend')),  # 修改密码
    (r"/", UserListHandler, get_provider('backend')),  # 用户列表
    (r"/(.*)", UserHandler, get_provider('frontend')),  # 用户操作
]
