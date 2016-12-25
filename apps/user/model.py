# -*- coding:utf-8 -*-

import projects.apps.base.model as model
import projects.libs.utils as utils

import oauth2
from projects.vendor.wxpay import wxpay
from projects.libs.oauthlib import save_token


class UserModel(model.StandCURDModel, model.Singleton):
    _name = "projects.user"

    def __init__(self):
        self.oauth_coll = model.BaseModel.get_model("oauth.OauthClientsModel").get_coll()
        super(UserModel, self).__init__()

    def init(self):
        count = self.coll.find({}).count()
        if count == 0:
            user = {
                "holder_id": None,
                "unionid": None,
                "enable_flag": 1,
                "wx_user": None,
                "permission": "admin",
                "system": "base",
                "mobile": "admin",
                "password": "962f352484a44a6a76f89f76ea418a62",
                "email": None,
                "login_name": "Admin",
                "login_time": utils.get_now(),
                "inviter_id": None,
                "role": [

                ],
                "add_time": utils.get_now(),
                "id_card": None,
                "name": "Admin"
            }
            self.coll.save(user)
            self._oauth2_register(utils.objectid_str(user['_id']),'962f352484a44a6a76f89f76ea418a62')
            # scopes = model.BaseModel.get_model("scope.ScopeModel").get_roles('base_superuser','base')
            # self.get_oauth2_token(utils.objectid_str(user['_id']),scopes=scopes)

            # 生成用户

    def new(self):
        user = None
        wx_user = None
        code = self.get_argument("code")
        mobile = self.get_argument("mobile")
        password = utils.md5(self.get_argument("password"))
        system = self._get_system()

        self._validate_inviter()

        if code is not None:
            js_pub = wxpay.JsApi_pub()
            js_pub.setCode(code)
            wx_user = js_pub.get_user_info()

        if wx_user is None and (mobile is None or password is None):
            raise ValueError(u"用户资料不完全")

        # 微信用户
        if wx_user is not None:
            if self.coll.find_one({"wx_user.unionid": wx_user.get("unionid", ''), "system": system}) is not None:
                user = self._update(wx_user, system)
            else:
                self._arguments['login_name'] = wx_user['nickname']
                self._arguments['unionid'] = wx_user.get("unionid", None)
                self._arguments['wx_user'] = wx_user
                user = self._create()

        # 手机用户
        if mobile is not None:
            user = self.coll.find_one({"mobile": mobile, "system": system})
            if user is not None:
                raise ValueError(u"该手机号已注册")
            else:
                self._arguments['login_name'] = u"%s****%s" % (mobile[0:3], mobile[-3:])
                user = self._create()
        if user is None:
            raise ValueError(u"用户创建失败")
        return utils.dump(user)

    def _validate_inviter(self):
        inviter_id = self.get_argument("inviter_id")
        if inviter_id is not None:
            if not self.is_exist(inviter_id):
                raise ValueError(u"邀请人不存在")

    # 获取角色
    def _get_role(self):
        role_list = ['normal', 'admin']
        role = self.get_argument("role", '')
        _roles = role.split(',')
        roles = []
        for r in _roles:
            if r in role_list:
                roles.append(r)
        return roles

    # 获取权限
    def _get_permission(self):
        permission_list = ['normal', 'admin']
        permission = self.get_argument("permission")
        if permission not in permission_list:
            return 'normal'
        else:
            return permission

    # 获取系统
    def _get_system(self, scope=None):
        scope_coll = model.BaseModel.get_model("scope.ScopeModel").coll
        if scope is None:
            scope = self.get_argument("scope")
        _s = scope_coll.find_one({"name": scope})
        if _s is None:
            raise ValueError(u"不允许的用户类型")
        else:
            return _s['system']

    # 注册用户进oauth2
    def _oauth2_register(self,id=None,password=None):
        if id is None and password is None:
            id = self.get_argument("_id")
            password = self.get_argument("password", "")
        oauth_user = self.oauth_coll.find_one({"identifier": id})
        if oauth_user is None:
            self.oauth_coll.save({'identifier': id,
                                  'secret': password,
                                  'redirect_uris': [],
                                  'authorized_grants': [oauth2.grant.ClientCredentialsGrant.grant_type]})

    # 获取oauth2的token
    def get_oauth2_token(self, client_id, scopes):
        return save_token(client_id, oauth2.grant.ClientCredentialsGrant.grant_type, client_id, scopes=[scopes])

    # 新建用户
    def _create(self):
        system = self._get_system()
        user = {
            "login_name": self.get_argument("login_name"),
            "mobile": self.get_argument("mobile"),
            "password": utils.md5(self.get_argument("password", "")),
            "role": self._get_role(),
            "permission": self._get_permission(),
            "unionid": self.get_argument("unionid"),
            "inviter_id": self.get_argument("inviter_id"),
            "wx_user": self.get_argument("wx_user"),
            "enable_flag": 1,
            "add_time": utils.get_now(),
            "name": self.get_argument("name"),
            "id_card": self.get_argument("id_card"),
            "holder_id": self.get_argument("holder_id"),
            "system": system,
            "email": self.get_argument("email"),
            "login_time": utils.get_now(),
        }

        self.coll.save(user)
        self._arguments['_id'] = utils.objectid_str(user['_id'])
        self._oauth2_register(utils.objectid_str(user['_id']),utils.md5(self.get_argument("password", "")))
        user['token'] = self.get_oauth2_token(utils.objectid_str(user['_id']), self.get_argument("scope"))
        del user['password']
        return utils.dump(user)

    def _update(self, wx_user, system):
        user = self.coll.find_one({"wx_user.unionid": wx_user['unionid'], "system": system})
        if user is not None:
            user['wx_user'] = wx_user
            user['login_time'] = utils.get_now()
            self.coll.save(user)
            user['token'] = self.get_oauth2_token(utils.objectid_str(user['_id']), self.get_argument("scope"))
            del user['password']
            return utils.dump(user)
        return None

    def login(self, mobile, password, scope):
        system = self._get_system(scope)
        if mobile is None or password is None:
            raise ValueError(u"用户或者密码为空")

        user = self.coll.find_one({"mobile": mobile, "password": utils.md5(password), "system": system, "enable_flag": 1})
        if user is None:
            raise ValueError(u"用户或者密码错误")
        user['login_time'] = utils.get_now()
        self.coll.save(user)

        user['token'] = self.get_oauth2_token(utils.objectid_str(user['_id']), scope)
        del user['password']
        return utils.dump(user)

    def changepwd(self, mobile, newpassword, scope):
        system = self._get_system(scope)
        if mobile is None or newpassword is None:
            raise ValueError(u"用户或者密码为空")

        user = self.coll.find_one({"mobile": mobile, "system": system})
        if user is None:
            raise ValueError(u"用户不存在")

        user['password'] = utils.md5(newpassword)
        self.coll.save(user)
        oauth = self.oauth_coll.find_one({"identifier": utils.objectid_str(user['_id'])})
        if oauth is None:
            raise ValueError(u"认证修改失败")
        oauth['secret'] = utils.md5(newpassword)
        self.oauth_coll.save(oauth)

        return utils.dump(user)
