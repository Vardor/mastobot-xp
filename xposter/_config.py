#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 19:47:19 2024

@author: carlos
"""
from schema import Schema, SchemaError, Regex, Or, Optional
import yaml

config_schema = Schema({
    "mastodon": {
        "instance": Or(
            Regex('^(?:[\w-]+\.)+[a-z]+$'), 
            error ="Error: 'instance' invalid format"),
        "token": str
        },
    "twitter":{
        "client_id": str,
        "client_secret": str,
        "redirect_uri": Regex('^https?:\/\/(?:(?:(?:[\w-]+\.)+[a-z]+)|(?:(?:(?:25[0-5]|(?:2[0-4]|1\d|[1-9]|)\d)\.?){4}))(?::\d+)?(?:\/\w+)*$')
        },
    "app":{
        "max_statuses": int,
        "interval": int,
        Optional("noxp"): [ Regex('^#\w+$') ],
        Optional("xp_boosts"): [ Regex('^@\w+@(?:[\w-]+\.)+[a-z]+$') ],
        Optional("xp_replies"): [ Regex('^@\w+@(?:[\w-]+\.)+[a-z]+$') ],
        Optional("autostart"): bool
            }
    
})

def validate_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
        
    try:
        config_schema.validate(config)
        return True, config
    except SchemaError as se:
        raise se  