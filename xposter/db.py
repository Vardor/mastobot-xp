#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 14:22:37 2024

@author: carlos
"""

import sqlite3

class MastoDB:
    def __init__(self, file):
        self.db = file

    def create_db(self):
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        query_pfx = "CREATE TABLE IF NOT EXISTS "
        #Create table <mastodon>
        query_table = "mastodon "
        query_bdy = '''(userid TEXT, username TEXT,instance TEXT,
                        PRIMARY KEY(userid))'''
        cur.execute(query_pfx + query_table + query_bdy)
        #Create table <twitter>
        query_table = "twitter "
        query_bdy = '''(userid TEXT PRIMARY KEY, 
                        username TEXT,
                        token TEXT,
                        refresh_token TEXT,
                        mastodon_userid, 
                        FOREIGN KEY (mastodon_userid) REFERENCES mastodon(userid))'''
        cur.execute(query_pfx + query_table + query_bdy)
        #Create table <xposts>
        query_table = "xposts "
        query_bdy = '''(mastodon_id TEXT PRIMARY KEY, twitter_id TEXT,
                        mastodon_userid, FOREIGN KEY (mastodon_userid)
                        REFERENCES mastodon (userid))'''
        cur.execute(query_pfx + query_table + query_bdy)
        
        connection.commit()
        connection.close()

    def insert_mastodon_db(self, m_id, m_name, m_instance):
        query_pfx = r"INSERT OR IGNORE INTO mastodon(userid, username, instance)"
        query_bdy = f''' VALUES('{m_id}', '{m_name}', '{m_instance}')'''
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        cur.execute(query_pfx + query_bdy)
        connection.commit()
        connection.close()
        
    def query_mastodon_db(self, userid):
        query = f'''SELECT * FROM mastodon WHERE userid=\'{userid}\''''
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        cur.execute(query)
        r = cur.fetchall()
        connection.close()
        return r

    def get_last_id(self):
        query = "SELECT * FROM xposts WHERE ROWID IN (SELECT max(ROWID) FROM xposts)"
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        cur.execute(query)
        r = cur.fetchone()
        connection.close()
        if r: return r[0]
        else: return None
        
    def get_xpost(self, m_id):
        query = f"SELECT * FROM xposts WHERE mastodon_id=\'{m_id}\'"
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        cur.execute(query)
        r = cur.fetchone()
        connection.close()
        return r
    
    def insert_xpost(self, m_id, t_id, m_userid):
        query_pfx = r"INSERT INTO xposts(mastodon_id, twitter_id, mastodon_userid)"
        query_bdy = f" VALUES('{m_id}', '{t_id}', '{m_userid}')"
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        cur.execute(query_pfx + query_bdy)
        connection.commit()
        connection.close()
        
    def get_twitter_account(self):
        query = "SELECT * FROM twitter"
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        cur.execute(query)
        r = cur.fetchone()
        connection.close()
        return r
    
    def update_twitter_account(self, token, userid):
        query_pfx = "UPDATE twitter SET "
        query_bdy = f"token = \'{token['access_token']}\', refresh_token = \'{token['refresh_token']}\' "
        query_sfx = f"WHERE userid = \'{userid}\'"
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        cur.execute(query_pfx + query_bdy + query_sfx)
        connection.commit()
        connection.close()
        
    def insert_twitter_account(self, userid, username, m_userid):
        query = f"""INSERT INTO twitter (userid, username, mastodon_userid)
                VALUES (\'{userid}\',\'{username}\',\'{m_userid}\')
                ON CONFLICT(userid) DO UPDATE SET
                mastodon_userid=excluded.mastodon_userid
                WHERE twitter.mastodon_userid!=excluded.mastodon_userid"""
        connection = sqlite3.connect(self.db)
        cur = connection.cursor()
        cur.execute(query)
        connection.commit()
        connection.close()

         