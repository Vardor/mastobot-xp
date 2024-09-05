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

def xpost(conf, db_file):
    logging.info("Starting mastobot-xp...")

    # set mastodon object
    m = Mastobot(conf['mastodon']['instance'])
    m.set_token(conf['mastodon']['token'])
            
    # set mastodb object
    db = MastoDB(db_file)
    
    exclude_replies = 'true'
    if conf['app']['xp_replies']: 
        xp_replies_ids = []
        for user in conf['app']['xp_replies']:
            user_id = m.get_user_id(user)
            if user_id: xp_replies_ids.append(user_id)
        if xp_replies_ids: exclude_replies = 'false'
    
    exclude_boosts = 'true'
    # WIP: enable xprost retoots
    # if conf['app']['xp_boosts']:
    #     xp_boosts_ids = []
    #     for user in conf['app']['xp_boosts']:
    #         user_id = m.get_user_id(user)
    #         if user_id: xp_boosts_ids.append(user_id)
    #     if xp_boosts_ids: exclude_boosts = 'false'

    statuses_list = m.get_statuses(exclude_replies=exclude_replies, exclude_boosts=exclude_boosts)
    xp_statuses = []
    
    #iterate to get all status to crosspost and store in a list
    statuses_count = 0      
    for status in statuses_list:
        current_id = str(status['id'])        
        if db.get_xpost(current_id) or statuses_count >= conf['app']['max_statuses']: break
        toot = Toot(status)
        if not(any(b in toot.clear_text for b in conf['app']['noxp']) or status['visibility'] != 'public'):
            
            # WIP: enable xprost retoots
            # if status['reblog']: 
            #     if status['reblog']['account']['id'] in xp_boosts_ids: 
            #         toot = m.get_status_by_id(m.get_status_by_id)
            #         xp_statuses.insert(0, toot)
            #         statuses_count += 1
            
            if ( (exclude_replies == 'true' and exclude_boosts == 'true')
                or (status['in_reply_to_account_id'] == m.userid)
                or (not status['in_reply_to_account_id']) 
                or (status['in_reply_to_account_id'] in xp_replies_ids) ):
                xp_statuses.insert(0, toot)
                statuses_count += 1
      
    if xp_statuses:
        t_account = db.get_twitter_account()
        t = TwitterApp(client_id=conf['twitter']['client_id'])
        token = t.refresh_token(t_account[3])
        db.update_twitter_account(token, t_account[0])
        
        for xp in xp_statuses:
            text = xp.get_short_text() + "\n\n" + xp.url
            
            # get reply_id if it is a reply
            if xp.is_self_reply():
                xpost = db.get_xpost(xp.in_reply_to_id) 
                if xpost: reply_id = xpost[1]
                else: reply_id  = None
            elif xp.in_reply_to_id:
                replied_status = m.get_status_by_id(xp.in_reply_to_id)
                replied_toot = Toot(replied_status)
                reply_id = replied_toot.tw_id   
                if not reply_id: continue
            else:
                reply_id = xp.tw_reply_id

            # set quote_id (default=None)
            quote_id = xp.tw_quote_id
                
            resp = t.post_tweet(text, reply_id=reply_id, quote_id=quote_id ) #post tweet
            if resp.status_code == 201:
                # create db entry 
                m_id = xp.id
                t_id = resp.json()['data']['id']
                m_userid = m.userid
                db.insert_xpost(m_id, t_id, m_userid)
                logging.info (f"posted to twitter: {t_id}")
            else: logging.info (f"could not post to twitter: {xp.id} reason:{resp.text}")

    logging.info("finished this cycle")


