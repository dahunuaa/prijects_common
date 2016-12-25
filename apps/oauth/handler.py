# -*- coding: utf-8 -*-

"""
    alter by: youfaNi
    alter on 2016-07-13
"""

from oauth2.web.tornado import OAuth2Handler

from projects.libs.oauthlib import get_provider

handlers = [
    (r'/token', OAuth2Handler, get_provider()),
]
