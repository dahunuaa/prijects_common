# -*- coding: utf-8 -*-

"""
    author : youfaNi
    date : 2016-07-13
"""

import projects.apps.base.model as model


class OauthClientsModel(model.BaseModel, model.Singleton):
    _name = "projects.oauth_clients"


class OauthAccessTokenModel(model.BaseModel, model.Singleton):
    _name = "projects.oauth_access_token"

