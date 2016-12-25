# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import APIHandler,TokenHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

class AdminOrganizationHandler(APIHandler,TokenHandler):
    pass

class AdminOrganizationListHandler(APIHandler,TokenHandler):
    pass

handlers = [
            (r"/", AdminOrganizationListHandler,get_provider('backend')),#用户列表
            (r"/(.*)",AdminOrganizationHandler ,get_provider('backend')),#用户操作
            ]
