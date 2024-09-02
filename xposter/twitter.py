#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 00:23:29 2024

@author: carlos
"""

import base64
import hashlib
import os
import re
import requests
from requests_oauthlib import OAuth2Session

class TwitterApp(OAuth2Session):
    __auth_url = 'https://twitter.com/i/oauth2/authorize'
    __token_url = "https://api.twitter.com/2/oauth2/token"
    
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, 
                 scope=None, token=None):
        OAuth2Session.__init__(self, client_id=client_id,
                               redirect_uri=redirect_uri,scope=scope,token=token)
        if client_secret: self.client_secret = client_secret
    
    def authorization_url(self):
        # Create a code verifier
        code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
        code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
        # Create a code challenge
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.replace("=", "")
        self.code_verifier = code_verifier
        self.code_challenge = code_challenge
        return OAuth2Session.authorization_url(self,self.__auth_url,
                                               code_challenge=self.code_challenge,
                                               code_challenge_method="S256")
    
    def fetch_token(self,code):
        return OAuth2Session.fetch_token(self,token_url=self.__token_url,
                                         client_secret=self.client_secret,
                                         code_verifier=self.code_verifier,
                                         code=code)
    
    def refresh_token(self,refresh_token=None, client_id=None):
        if not client_id: client_id=self.client_id
        try:
            token = OAuth2Session.refresh_token(self,
                                               token_url=self.__token_url,
                                               client_id=client_id,
                                               refresh_token=refresh_token)
        except:
            token = None
        return token
    
    def post_tweet(self, text, reply_id=None, quote_id=None, token=None):
        data = {"text": text}
        if reply_id: data["reply"] = {"in_reply_to_tweet_id": reply_id}
        if quote_id: data['quote_tweet_id'] = quote_id
        if not token: token = self.token
        headers={ "Authorization": "Bearer {}".format(token["access_token"]),
                "Content-Type": "application/json" }
        r = requests.post("https://api.twitter.com/2/tweets", 
                          json=data, headers=headers)
        return r

    def get_tweet(self, tuit_id, token=None):
        data = {"ids": tuit_id}
        if not token: token = self.token
        headers= {"Authorization": "Bearer {}".format(token["access_token"]),}
        r = requests.get("https://api.twitter.com/2/tweets", params=data, headers=headers)
        return r
    
    def whoami(self,access_token=None):
        if not access_token: access_token = self.token["access_token"]
        user = requests.get( "https://api.twitter.com/2/users/me",
        headers={"Authorization": "Bearer {}".format(access_token)}).json()
        return user

