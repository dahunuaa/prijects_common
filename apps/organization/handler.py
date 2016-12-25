# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-20
"""

from projects.apps.base.handler import TokenHandler, SingleStandardHanler, MultiStandardHandler
from projects.libs.loglib import get_logger
from projects.libs.oauthlib import get_provider

logger = get_logger("debug")


class OrganizationListHandler(MultiStandardHandler, TokenHandler):
    _model = "organization.OrganizationModel"


class OrganizationHandler(SingleStandardHanler, TokenHandler):
    _model = "organization.OrganizationModel"


handlers = [
    (r"", OrganizationListHandler, get_provider('admin')),
    (r"/(.*)", OrganizationHandler, get_provider('frontend')),
]
