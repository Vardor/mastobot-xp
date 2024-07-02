#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 18:42:10 2024

@author: carlos
"""

import requests
import json 
import re
import yaml
import os
from time import sleep
from bs4 import BeautifulSoup

data_dir = '/data'
config_file = 'config.yml'
db_file = '.last_status'

######################################################################
## Search toots from user

def get_user_statuses(instance, user_id, user_token, limit):
    base_endpoint = '/api/v1/accounts'
    endpoint = base_endpoint + '/' + str(user_id) + '/statuses'
    headers = {'Authorization': 'Bearer ' + user_token}
    q_data = {
       'exclude_reblogs': True,
       'exclude_replies': True,
       'limit': limit
        }
    q_url = "https://" + instance + endpoint 
    r = requests.get(q_url, params=q_data, headers=headers) # request user posts
    r_data = json.loads(r.text) #list of toots
    return r_data

######################################################################
## REMOVE HTML FROM TEXT

def clean_status_text(text):
    text = re.sub(r'<br(?: \/)?>','\n', text) #replace <br> with \n
    soup = BeautifulSoup(text, 'html.parser')
    text = ''
    for p in soup.find_all('p'):
        text = text + p.text + '\n\n'
    text = re.sub(r'(@\w+)@(?:x\.com|twitter\.com|birdsite\.com)', r'\1', text).strip()
    return text

######################################################################
## Limit chars in text

def short_text(text, limit):
    if len(text) > limit:
        #cut in <limit> chars, but removes last incomplete word
        text = text[:limit].rsplit(None, 1)[0] + '...'
    return text

######################################################################
## POST TWEET WITH N8N WEBHOOK

def post_to_x(status, status_url, q_url, key, val):
    headers = {key:val}
    q_data = {
        "text": status,
        "url" : status_url,
        "reply_id": ""
        }
    r = requests.post(q_url, params=q_data, headers=headers)
    r_data = json.loads(r.text) #post to x and get response
    return r_data

def main():
    print("starting main...")
     
    # Load config file and assign values to vars
    with open(data_dir + '/' + config_file, 'r') as f:
        config = yaml.safe_load(f)             
    instance = config['app']['instance']
    client_id = config['app']['client_id']
    client_secret =  config['app']['client_secret']
    interval = config['app']['interval']
    no_xp = config['app']['noxp']
    user = config['user']['username']
    user_id = config['user']['id']
    user_token = config['user']['token']
    max_statuses = config['user']['max_statuses']
    wh_url = config['webhook']['url']
    wh_key = config['webhook']['key']
    wh_val = config['webhook']['val']
    
    last_status_file = data_dir + '/' + db_file

    if not os.path.exists(last_status_file): # check if last_status file exists
        open(last_status_file, 'a').close() #create file
         
    while 1:
        #print("starting while...")
        statuses_list = get_user_statuses(instance, user_id, user_token, max_statuses)
        if type(statuses_list) != list:
            interval_ori = interval
            interval = interval*2
            continue
        elif 'interval_ori' in locals():
            interval = interval_ori
            del interval_ori
            
        with open(last_status_file,'r') as f:
            last_status_id = f.readline()
            last_status_id = last_status_id.strip()
            last_status_xp = last_status_id
            f.close()
        xp_statuses = []
        
        #iterate to get all status to crosspost
        for status in statuses_list:
            current_id = str(status['id'])
            if current_id == last_status_id: break   
            content = clean_status_text(status['content'])
            if not(any(b in content for b in no_xp) or status['visibility'] != 'public'):
                url = status['url']
                xp = {
                    'id': current_id,
                    'status': content,
                    'url': url }      
                xp_statuses.insert(0, xp)
          
        if xp_statuses != []:
            for xp in xp_statuses:
                x_text = short_text(xp['status'],250) # limit to 250 chars for X
                tuit = post_to_x(x_text, xp['url'], wh_url, wh_key, wh_val)
                print (tuit)
                last_status_xp = xp['id']
            
            if last_status_xp != last_status_id:
                f = open(last_status_file, "r+")
                f.write(last_status_xp)
                f.close()

        #print("executed")
        sleep(interval*60)
        #sleep(1*60)

main()