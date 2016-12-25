# -*- coding: utf-8 -*-

"""
    alter by: Daemon
    alter on 2016-09-27
"""

import oauth2
import oauth2.tokengenerator
import oauth2.grant
import oauth2.store.redisdb
import oauth2.store.mongodb

import time

from oauth2.datatype import AccessToken
from projects.apps.base import model
from projects.libs import utils
from projects.libs.options import config

# Populate mock
oauth_client_coll = model.BaseModel.get_model("oauth.OauthClientsModel").coll
client_store = oauth2.store.mongodb.ClientStore(oauth_client_coll)

oauth_access_token_coll = model.BaseModel.get_model("oauth.OauthAccessTokenModel").coll
token_store = oauth2.store.mongodb.AccessTokenStore(collection=oauth_access_token_coll)

# Redis for tokens storage
auth_code_store = oauth2.store.AuthCodeStore()

# Generator of tokens
token_generator = oauth2.tokengenerator.Uuid4()
token_generator.expires_in[oauth2.grant.ClientCredentialsGrant.grant_type] = 3600 * config.default_expired_time


def get_provider(role="frontend"):
    # OAuth2 controller
    auth_provider = oauth2.Provider(
            access_token_store=token_store,
            auth_code_store=auth_code_store,
            client_store=client_store,
            token_generator=token_generator
    )
    auth_provider.token_path = '/api/oauth/token'

    # scope_model = model.BaseModel.get_model("scope.ScopeModel")
    # scopes = [s['name'] for s in scope_model.get_allow_scopes(role)]

    default_scope = role
    scopes = []
    # Add Client Credentials to OAuth2 controller
    auth_provider.add_grant(oauth2.grant.ClientCredentialsGrant(default_scope=default_scope, scopes=scopes))

    return auth_provider


def save_token(client_id, grant_type, user_id, scopes=[], expires_at=int(time.time()) + token_generator.expires_in[
    oauth2.grant.ClientCredentialsGrant.grant_type]):
    coll = token_store.collection
    access_token_store = token_store
    token_str = token_generator.generate()
    token = AccessToken(client_id=client_id, grant_type=grant_type, token=token_str, data={}, expires_at=expires_at,
                        refresh_token=None, refresh_expires_at=None, scopes=scopes,
                        user_id=user_id)
    coll.remove({"client_id": client_id})
    if access_token_store.save_token(token):
        return token_str
    else:
        raise ValueError(u"生成token失败")


def validate_token(token_str, system):
    coll = token_store.collection
    token = coll.find_one({
        "token": token_str,
    },sort=[("expires_at", -1)])

    if token is None:
        raise Exception('Invalid Token')

    if token['expires_at'] <= int(time.time()):
        raise Exception('expired token')

    flag = False
    for t in token['scopes']:
        if t in system:
            flag = True
    if not flag:
        raise Exception('Permission denied')

    return utils.dump(token)
