import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, session, request
from xposter.xposter import load_config, xpost
from xposter.xposter import Mastobot
from xposter.twitter import TwitterApp
from xposter.db import MastoDB

app = Flask(__name__)
app.secret_key = os.urandom(50)

# Set the scopes
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]

CONFIG_FILE = 'config.yml'
DATA_DIR = 'data/'
DB_FILE = '.mastobot.db'

db_file = DATA_DIR + DB_FILE

##################### set logging config #############################
logging.basicConfig(
    level=logging.INFO, #INFO
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
######################################################################

################### INITIAL SETUP #################
# Load config
conf = load_config(CONFIG_FILE)
logging.debug("config loaded {}".format(conf))

# initialize db
db = MastoDB(db_file)
db.create_db()

# check and store mastodon account information
m = Mastobot(conf['mastodon']['instance'])
m.set_token(token=conf['mastodon']['token'])
db.insert_mastodon_db(m.userid,m.username,m.instance)

# check for twitter account information
t_account = db.get_twitter_account()

# start scheduler
scheduler = BackgroundScheduler()
scheduler.start()

if t_account:
    xpost_job = scheduler.add_job(xpost,args=[conf,db_file],trigger='interval',minutes=conf['app']['interval'])
    logging.info("added job to scheduler")
    if not conf['app'].get('autostart'):  xpost_job.pause()

################# TEST SCHEDULER ##################

# scheduler.add_job(job)
# scheduler.add_job(job, 'interval', seconds=10)
# scheduler.start()

# @app.before_request
# def start_scheduler():
#     scheduler.start()
    
# scheduler.shutdown() # stop scheduler

##################################################

@app.route("/")
def demo():
    global twitter
    jobs = scheduler.get_jobs()
    if jobs:
        if jobs[0].next_run_time:
            return "running..."
        else:
            return "stopped..."
    else:
        if t_account:
            #t = TwitterApp(conf['twitter']['client_id'])
            #token = t.refresh_token(t_account[3])
            return "stopped 2"
        else:
            twitter = TwitterApp(conf['twitter']['client_id'], client_secret=conf['twitter']['client_secret'],
                                 redirect_uri=conf['twitter']['redirect_uri'], scope=scopes)
            authorization_url, state = twitter.authorization_url() 
            session["oauth_state"] = state
            return redirect(authorization_url)


@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    token = twitter.fetch_token(code)
    user = twitter.whoami()
    db.insert_twitter_account(user['data']['id'], user['data']['name'], m.userid)
    db.update_twitter_account(token, user['data']['id'])
    global xpost_job
    xpost_job = scheduler.add_job(xpost,args=[conf,db_file],trigger='interval',minutes=conf['app']['interval'])
    return token

if __name__ == "__main__":
    app.run()