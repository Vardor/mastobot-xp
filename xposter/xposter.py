#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 18:42:10 2024

@author: carlos
"""

import yaml
import logging
from xposter.mastodon import Mastobot, Toot
from xposter.twitter import TwitterApp
from xposter.db import MastoDB

DATA_DIR = 'data'
DB_FILE = '.mastobot.db'
dbFile = DATA_DIR + "/" + DB_FILE

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

def xpost(conf):
    logging.info("Starting mastobot-xp...")
     
    # Load config file
    # conf = load_config(DATA_DIR + "/" + CONFIG_FILE)
    
   
    # set mastodon object
    m = Mastobot(conf['mastodon']['instance'])
    m.set_token(conf['mastodon']['token'])
            
    # set mastodb object
    db = MastoDB(dbFile)

    last_status_id = db.get_last_id()
    
    xp_statuses = []
    
    statuses_list = m.get_statuses()
    
    #iterate to get all status to crosspost and store in a list
    for status in statuses_list:
        current_id = str(status['id'])
        if current_id == last_status_id: break
        toot = Toot(current_id,status['url'],status['content'])
        if not(any(b in toot.clear_text for b in conf['app']['noxp']) or status['visibility'] != 'public'):
            xp_statuses.insert(0, toot)
      
    if xp_statuses:
        t_account = db.get_twitter_account()
        t = TwitterApp(client_id=conf['twitter']['client_id'])
        token = t.refresh_token(t_account[3])
        db.update_twitter_account(token, t_account[0])
        
        for xp in xp_statuses:
            text = xp.get_short_text() + "\n\n" + xp.url
            reply_id = xp.tw_reply_id
            resp = t.post_tweet(text, reply_id) #post tweet
            if resp.status_code == 201:
                # create db entry 
                m_id = xp.id
                t_id = resp.json()['data']['id']
                m_userid = m.userid
                db.insert_xpost(m_id, t_id, m_userid)
            logging.info (f"posting to twitter: {t_id}")
        

    logging.info("finished this cycle")


