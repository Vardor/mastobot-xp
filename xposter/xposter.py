#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 21:00:44 2024

@author: carlos
"""

import re
from bs4 import BeautifulSoup

class Toot:
    def __init__(self,status_id,url,content):
        self.id = status_id
        self.url = url
        self.text = content
        self.tw_reply_id = ""
        self.clear_text = self.clean_status_text()
        self.max_tw_len = 250 + self.get_tw_len_dif()
        
    def clean_status_text(self):
        text = re.sub(r'<br(?: \/)?>','\n', self.text) #replace <br> with \n
        soup = BeautifulSoup(text, 'html.parser')
        text = ""
        for p in soup.find_all('p'):
            text = text + p.text + "\n\n"
        text = re.sub(r"(@\w+)@(?:x\.com|twitter\.com|birdsite\.com)", r"\1", text).strip()
        return text
    
    def short_text(self, limit):
        if len(self.clear_text) > limit:
            #cut in <limit> chars, but removes last incomplete word
            text = self.clear_text[:limit].rsplit(None, 1)[0] + "..."
        return text
    
    def is_x_reply(self):
        regex = r're:\shttps?:\/\/(?:farside\.link\/(?:https?:\/\/)?)?(?:x.com|twitter.com|[bn]itter.altgr.xyz|nitter.poast.org|xcancel.com)\/\w+\/\w+\/(\d+).*'
        m = re.search(regex, self.clear_text, re.IGNORECASE)
        if m:
            self.tw_reply_id = m.group(1)
            new_text = re.sub(rf'{m.group(0)}', '', self.clear_text)
            self.clear_text = new_text
            self.max_tw_len += 27 
            return True
        else:
            return False
        
    def get_tw_len_dif(self):
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