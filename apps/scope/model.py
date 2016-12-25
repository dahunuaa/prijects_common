# -*- coding:utf-8 -*-

import projects.apps.base.model as model
from projects.libs.datatypelib import *


class ScopeModel(model.StandCURDModel, model.Singleton):
    _name = "projects.scope"
    _columns = [
        ("system", StrDT(required=True)),
        ("roles", ListDT(required=True)),
        ("name", StrDT(required=True)),
    ]

    def init(self):
        count = self.coll.find({}).count()
        if count == 0:
            init_scope = {
                "name": self.config("init_scope").name,
                "system": self.config("init_scope").system,
                "roles": self.config("init_scope").roles,
                "add_time": utils.get_now(),
                "last_updated_user": "",
                "delete_user_id": "",
                "add_user_id": "",
                "last_updated_time": "",
            }
            object = self._new()
            object.update(init_scope)
            self.coll.save(object)

    def before_create(self, object):
        roles = self.get_argument("roles", '')
        scope_roles = self.config("scope_roles")
        name = self.get_argument("name")
        system = self.get_argument("system")
        for r in roles:
            if r not in scope_roles:
                raise ValueError("Scope[%s]的角色[%s]错误" % (name, r))

        if system not in self.config("systems"):
            raise ValueError(u"Scope[%s]的系统[%s]错误" % (name, system))

        if self.coll.find({"name":name}).count() != 0:
            raise ValueError(u"Scope[%s]已存在"%name)
        return object

    def get_roles(self,name,system):
        scope = self.coll.find_one({"name":name,"system":system})
        if scope is None:
            return None
        else:
            return scope['roles']

    def get_allow_scopes(self,rolename):
        scopes = self.coll.aggregate([
            {"$unwind": "$roles"},
            {"$match": {"roles": rolename,"enable_flag":1}},
            {"$project":{"name": "$name"}},
        ])
        return utils.dump(scopes)

    def get_all_scopes(self):
        scopes = self.coll.find({"enable_flag":1})
        return utils.dump(scopes)
