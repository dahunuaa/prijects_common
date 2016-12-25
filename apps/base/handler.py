# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#

import traceback
import logging
import logging.config
import json
import datetime
import functools
import tornado.locale
import tornado.web
import tornado.gen

from tornado import escape
from tornado.web import RequestHandler as BaseRequestHandler, HTTPError
from projects.bootstrap import exceptions
from projects.libs import utils
from projects.libs.oauthlib import validate_token
from projects.libs.asynclib import AsyncUtils
from projects.libs.options import config
from .model import BaseModel

try:
    import importlib
except:
    from projects.libs import importlib

async_server = AsyncUtils(100)


class Dict(dict):
    def __missing__(self, key):
        rv = self[key] = Dict()
        return rv

    def __setitem__(self, key, value):
        if key not in self:
            dict.__setitem__(self, key, value)


class BaseHandler(BaseRequestHandler):
    _model = None

    def initialize(self):
        self.set_model()
        super(BaseHandler, self).initialize()

    def set_model(self):
        self.model = BaseModel.get_model(self._model)
        if self.model is not None:
            self.coll = self.model.get_coll()
        else:
            self.coll = None

    def prepare(self):
        self.traffic_control()
        pass

    def traffic_control(self):
        # traffic control hooks for api call etc
        self.log_apicall()
        pass

    def log_apicall(self):
        pass

    def format_arguments(self):
        arguments = self.request.arguments
        obj = Dict()
        for (k, v) in arguments.items():
            try:
                exec("%s = '%s'" % (k, v[0].decode()))
            except UnicodeDecodeError as e:
                exec("%s = '%s'" % (k, v[0]))
            except Exception as e:
                print(e)
                pass
        return obj

    def format_request_params(self):
        arguments = self.request.arguments
        format_params = u""
        for (k, v) in arguments.items():
            try:
                if v[0].isdigit():
                    format_params += str("%s = '%s'," % (k, v[0]))
                    continue
                try:
                    format_params += str("%s = %s," % (k, json.loads(v[0].decode("utf-8"))))
                except:
                    format_params += str("%s = '%s'," % (k, v[0].decode("utf-8")))
            except UnicodeDecodeError as e:
                try:
                    temp = "%s = %s," % (k, json.loads(v[0]))
                except:
                    temp = "%s = '%s'," % (k, v[0])
                format_params += temp.decode("utf-8")
            except Exception as e:
                print(e)
                pass
        return format_params


class BaseAPIHandler(BaseHandler):
    def initialize(self):
        super(BaseAPIHandler, self).initialize()

    def prepare(self):
        self.vaildate_header()
        super(BaseAPIHandler, self).prepare()

    def vaildate_header(self):
        for k, v in self.request.headers.items():
            if k.startswith("Ig-"):
                if k == 'Ig-Sign':
                    if v != 'X-Requested-With':
                        self.set_status(401)
                        result = utils.reset_response_data(0, "用户账户有误")
                        self.set_header("Content-Type", "application/json; charset=UTF-8")
                        self.finish(result, status_code=401)


class APIHandler(BaseAPIHandler):
    result = utils.init_response_data()
    user_id = None
    system = None

    def set_result(self, code, e=None):
        self.result = utils.reset_response_data(0, str(e))

    def finish(self, chunk=None, notification=None, origin=False, status_code=200):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "X-Requested-With,Set-Cookie,Ig-Appid,Ig-Appsecret,Ig-Timestamp,Ig-Sign")
        self.set_header("Access-Control-Allow-Methods", "PUT,DELETE,POST,GET,PATCH")
        self.set_header('Content-type', 'application/x-www-form-urlencoded; charset=utf-8')
        # 设置header键值对
        if chunk is None:
            chunk = {}

        if isinstance(chunk, dict):  # chunk默认情况下给chunk一个dict地址值，并执行下列步骤
            if origin != True:
                chunk = {"meta": {"code": status_code}, "response": chunk}  # orgin默认情况下给chunk赋"meta"={"code":200}
                # "response"=上次的chunk的字典内容

            if notification:
                chunk["notification"] = {"message": notification}  # 如果notification有值则再chunk中添加notification键值对

        callback = escape.utf8(self.get_argument("callback", None))

        # self.set_header("Access-Control-Allow-Credentials",'true')

        if callback:
            self.set_header("Content-Type", "application/x-javascript; charset=utf-8;")

            if isinstance(chunk, dict):
                chunk = escape.json_encode(chunk)

            self._write_buffer = [callback, "(", chunk, ")"] if chunk else []
            super(APIHandler, self).finish()
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.set_header("Server", "projects API server/v0.1.0")
            super(APIHandler, self).finish(chunk)

    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages."""
        debug = self.settings.get("debug", False)
        try:
            exc_info = kwargs.pop('exc_info')
            e = exc_info[1]

            if isinstance(e, exceptions.HTTPAPIError):
                pass
            elif isinstance(e, HTTPError):
                e = exceptions.HTTPAPIError(e.status_code)
            else:
                e = exceptions.HTTPAPIError(500)

            exception = "".join([ln for ln in traceback.format_exception(*exc_info)])

            if status_code == 500 and not debug:
                # self._send_error_email(exception)
                e.response["exception"] = exception

            if debug:
                e.response["exception"] = exception

            self.clear()
            self.set_status(200)  # always return 200 OK for API errors
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.set_header("Server", "projects API server/v0.1.0")
            self.finish(str(e))
        except Exception:
            logging.error(traceback.format_exc())
            return super(APIHandler, self).write_error(status_code, **kwargs)


# 带加密字段的处理器
class TokenHandler(BaseAPIHandler):
    user_id = ""
    system = None

    def initialize(self, provider):
        self.provider = provider
        super(TokenHandler, self).initialize()

    # authenticate tokens
    def prepare(self):
        super(TokenHandler, self).prepare()
        try:
            token = self.get_argument('access_token', None)
            if not token:
                auth_header = self.request.headers.get('Authorization', None)
                if not auth_header:
                    raise Exception('This resource need a authorization token')
                token = auth_header
            scope_model = BaseModel.get_model("scope.ScopeModel")
            role = self.provider.grant_types[0].default_scope
            scopes = [s['name'] for s in scope_model.get_allow_scopes(role)]
            token = validate_token(token, scopes)
            self.user_id = token['user_id']
            scope_coll = scope_model.coll
            scope = scope_coll.find_one({"name":token['scopes'][0]})
            self.system = scope['system']
            self.scopes = scopes
        except Exception as err:
            self.set_header('Content-Type', 'application/json')
            self.set_status(401)
            result = utils.reset_response_data(0, str(err))
            self.finish(result, status_code=401)


class ErrorHandler(BaseAPIHandler):
    """Default 404: Not Found handler."""

    def prepare(self):
        super(ErrorHandler, self).prepare()
        raise HTTPError(404)


class APIErrorHandler(APIHandler):
    """Default API 404: Not Found handler."""

    def prepare(self):
        super(APIErrorHandler, self).prepare()
        raise exceptions.HTTPAPIError(404)


class BaseRenderHandler(BaseHandler):
    def initialize(self, locale='zh_CN'):
        tornado.locale.load_gettext_translations('./locales', 'messages')
        self.set_locale(locale)
        super(BaseRenderHandler, self).initialize()

    def set_locale(self, locale='zh_CN'):
        self.locale = tornado.locale.get(locale)
        self.locale.translate = tornado.locale.get(locale).translate


class SingleStandardHanler(APIHandler):
    # 根据_id获取元素
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, _id):
        try:
            self.model.set_request(self.request)
            self.model.set_id(_id)
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._get)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    # 根据_id修改
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def put(self, _id):
        try:
            self.model.set_request(self.request)
            self.model.set_id(_id)
            self.model.set_argument("last_updated_user_id", self.user_id)
            self.model.set_argument("last_updated_time", utils.get_now())
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._put)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    # post操作
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, _id):
        try:
            self.model.set_request(self.request)
            self.model.set_id(_id)
            self.model.set_argument("add_user_id", self.user_id)
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._post)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    # 根据_id删除
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self, _id):
        try:
            self.model.set_request(self.request)
            self.model.set_id(_id)
            self.model.set_argument("delete_user_id", self.user_id)
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._delete)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    # 返回服务器配置
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def options(self, _id):
        try:
            self.model.set_request(self.request)
            self.model.set_id(_id)
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._options)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    def _get(self):
        self.result['data'] = self.model.get()

    def _put(self):
        self.result['data'] = self.model.update()

    def _post(self):
        raise NotImplementedError(u"暂无此操作")

    def _delete(self):
        self.result['data'] = self.model.delete()

    def _options(self):
        self.result['data'] = self.model.config()


class MultiStandardHandler(APIHandler):
    # 根据条件获取元素列表
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            self.model.set_request(self.request)
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._get)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    # 新建
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        try:
            self.model.set_request(self.request)
            self.model.set_argument("add_user_id", self.user_id)
            self.model.set_argument("add_time", utils.get_now())
            self.model.set_argument("last_updated_time", utils.get_now())
            self.model.set_argument("last_updated_user_id", "")
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._post)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    # 批量修改
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def put(self):
        try:
            self.model.set_request(self.request)
            self.model.set_argument("last_updated_user_id", self.user_id)
            self.model.set_argument("last_updated_time", utils.get_now())
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._put)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    # 批量删除
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self):
        try:
            self.model.set_request(self.request)
            self.model.set_argument("delete_user_id", self.user_id)
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._delete)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    # 返回服务器配置
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def options(self):
        try:
            self.model.set_request(self.request)
            if self.model.get_argument("system",'') == '':
                self.model.set_argument("system", self.system)
            yield async_server.cmd(self._options)
        except Exception as e:
            self.set_result(0, str(e))
        self.finish(self.result)

    def _get(self):
        self.result['data'] = self.model.list()[0]
        self.result['pager'] = self.model.list()[1]

    def _post(self):
        self.result['data'] = self.model.create()

    def _put(self):
        self.result['data'] = self.model.update_many()

    def _delete(self):
        self.result['data'] = self.model.delete_many()

    def _options(self):
        self.result['data'] = self.model.config()
