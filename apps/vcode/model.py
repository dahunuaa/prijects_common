# -*- coding:utf-8 -*-

import projects.apps.base.model as model
import projects.libs.utils as utils
import datetime
from projects.libs.datatypelib import *


class VcodeModel(model.StandCURDModel, model.Singleton):
    _name = "projects.vcode"
    _columns = [
        ("type", StrDT(required=True)),
        ("to", StrDT(required=True)),
        ("code", StrDT()),
        ("expired_time", DatetimeDT()),
        ("used_time", StrDT()),
    ]

    def before_create(self, object):
        type = self.get_argument("type")
        to = self.get_argument("to")
        if type not in self.config("allow_types"):
            raise ValueError(u"不允许的验证码类型[%s]" % type)
        if type == 'sms':
            if not utils.check_mobile(to):
                raise ValueError("手机号[%s]格式有误" % to)
        elif type == 'email':
            if not utils.check_email(to):
                raise ValueError("邮箱[%s]格式有误" % to)
        object['code'], object['expired_time'] = self.send_code(type, to)
        return object

    def send_code(self, type, to):
        if self.validate_code_count(type, to):
            # TODO 根据type发动验证码
            code = utils.get_random_num(6, 'number')
            if type == 'sms':
                pass
            elif type == 'email':
                pass
            return code, datetime.datetime.now() + datetime.timedelta(minutes=self.config("default_expired_time"))
        else:
            raise ValueError(u"发送失败")

    # 验证验证码发送限制
    def validate_code_count(self, type, to):
        hourly_count = self.coll.find({"type": type, "to": to, "add_time": {
            "$gte": datetime.datetime.now() - datetime.timedelta(hours=1)}}).count()
        day_count = self.coll.find({"type": type, "to": to,
                                    "add_time": {"$gte": datetime.datetime.now() - datetime.timedelta(days=1)}}).count()

        if hourly_count >= self.config("max_msg_hourly"):
            raise ValueError(u"用户[%s]一小时内最多发送[%s]条验证码，请稍后再试" % (to, self.config("max_msg_hourly")))

        if day_count >= self.config("max_msg_day"):
            raise ValueError(u"用户[%s]一天内最多发送[%s]条验证码，请明天再试" % (to, self.config("max_msg_day")))

        if self.get_argument("system") not in self.config("systems"):
            raise ValueError(u"系统未开放验证码[%s]" % self.get_argument("system"))

        # 将过期的验证码的enable_flag改为0
        self.coll.update({"type": type, "to": to, "enable_flag": 1}, {"$set": {"enable_flag": 0}}, False, True
                         )
        return True

    def validate_code(self,code=None,to=None,system=None,use=None):
        code = self.get_argument("code") if code is None else code
        to = self.get_argument("to") if to is None else to
        system = self.get_argument("system") if system is None else system
        use = self.get_argument("use",True) if use is None else use
        use = True if use == "1" or use == 'True' else False

        enable_code = self.coll.find_one({"code": code, "to": to, "system": system, "enable_flag": 1})
        if code in self.config("pass_code"):
            return True

        if enable_code is None:
            raise ValueError(u"无效的验证码[%s]" % code)
        if datetime.datetime.now() > enable_code['expired_time']:
            raise ValueError(u"验证码已过期[%s]" % code)
        if use:
            enable_code['enable_flag'] = 0
            enable_code['used_time'] = utils.get_now()
            self.coll.save(enable_code)
        return True

