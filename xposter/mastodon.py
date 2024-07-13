#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 21:00:44 2024

@author: carlos
"""

import requests
import json
import re
from bs4 import BeautifulSoup

class Mastobot:
    def __init__(self, instance, token=None):
        self.instance = instance

    def __set_app_user(self):
        endpoint = "/api/v1/accounts/verify_credentials"
        headers = {'Authorization': 'Bearer ' + self.token}
        q_url = "https://" + self.instance + endpoint
        r = json.loads(requests.get(q_url, headers=headers).text)
        if r.get('id') and r.get('username') : 
            self.userid = r['id']
            self.username = r['username']
            return True
        else:
            return False
        
    def set_token(self, token):
        endpoint = "/api/v1/apps/verify_credentials"
        headers = {'Authorization': 'Bearer ' + token}
        q_url = "https://" + self.instance + endpoint
        r = json.loads(requests.get(q_url, headers=headers).text)
        if r.get('name'): 
            self.token = token
            self.__set_app_user()
            return f"Token succesfully validated for user @{self.username}@{self.instance}"
        elif r.get('error'): 
            return "Couldn't validate token. Check instance/token"
        
    def get_user_id(self,user_handle):
        endpoint = '/api/v1/accounts/lookup'
        headers = {'Authorization': 'Bearer ' + self.token}
        q_data = { 'acct': user_handle }
        q_url = "https://" + self.instance + endpoint 
        r = requests.get(q_url, params=q_data, headers=headers) # request user data   
        r_data = json.loads(r.text)
        if r_data.get('id'): return r_data['id']
        elif r_data.get('error'): return ""
        
    def get_statuses(self, limit=20, exclude_replies='true', exclude_boosts='true'):
        base_endpoint = '/api/v1/accounts'
        endpoint = base_endpoint + '/' + str(self.userid) + '/statuses'
        headers = {'Authorization': 'Bearer ' + self.token}
        q_data = {
           'exclude_reblogs': exclude_boosts,
           'exclude_replies': exclude_replies,
           'limit': limit
            }
        q_url = "https://" + self.instance + endpoint 
        r = requests.get(q_url, params=q_data, headers=headers) # request user posts
        return json.loads(r.text) #list of toots

class Toot:
    def __init__(self,status_id,url,content):
        self.id = status_id
        self.url = url
        self.text = content
        self.clear_text = self.__clean_status_text()
        self.tw_max_len = 250 + self.__get_tw_len_dif()
        self.tw_reply_id = self.__get_reply_id()
        
    def __clean_status_text(self):
        text = re.sub(r'<br(?: \/)?>','\n', self.text) #replace <br> with \n
        soup = BeautifulSoup(text, 'html.parser')
        text = ""
        for p in soup.find_all('p'):
            text = text + p.text + "\n\n"
        text = re.sub(r"(@\w+)@(?:x\.com|twitter\.com|birdsite\.com)", r"\1", text).strip()
        return text
    
    def __get_tw_len_dif(self):
        soup = BeautifulSoup(self.text, 'html.parser')
        q_links = 0
        l_links = 0
        for a in soup.find_all('a'):
            if not re.match('^(?:@|#)\w+', a.text):
                l_links = l_links + len(a.text)
                q_links +=1
        tw_len_dif = l_links - q_links*23 
        return tw_len_dif
        #max_len = 250 + tw_len_dif
        
    def __get_reply_id(self):
        regex = r're:\shttps?:\/\/(?:farside\.link\/(?:https?:\/\/)?)?(?:x.com|twitter.com|[bn]itter.altgr.xyz|nitter.poast.org|xcancel.com)\/\w+\/\w+\/(\d+).*'
        m = re.search(regex, self.clear_text, re.IGNORECASE)
        if m:
            tw_reply_id = m.group(1)
            new_text = re.sub(rf'{m.group(0)}', '', self.clear_text)
            self.clear_text = new_text
            self.tw_max_len -= 27 
            return tw_reply_id 
        else:
            return None
        
    def get_short_text(self):
        limit = self.tw_max_len
        if len(self.clear_text) > limit:
            #cut in <limit> chars, but removes last incomplete word
            text = self.clear_text[:limit].rsplit(None, 1)[0] + "..."
            return text
        else:
            return self.clear_text