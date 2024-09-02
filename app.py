import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, session, request, render_template
from xposter.xposter import load_config, xpost
from xposter.xposter import Mastobot
from xposter.twitter import TwitterApp
from xposter.db import MastoDB

app = Flask(__name__)
app.secret_key = os.urandom(50)

# Set the scopes for tw account
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
logging.info("config loaded succesfully")

# initialize db
db = MastoDB(db_file)
db.create_db()

# check and store mastodon account information
m = Mastobot(conf['mastodon']['instance'])
r = m.set_token(token=conf['mastodon']['token'])
if r[0]:
    db.insert_mastodon_db(m.userid,m.username,m.instance)
    valid_mastodon = r[1]
    valid_mastodon_reason = ""
    logging.info("Valid token for acoount {}".format(r[1]))
else: 
    valid_mastodon = ""
    valid_mastodon_reason = "Not valid mastodon token for instance {}".format(conf['mastodon']['instance'])
    logging.info(valid_mastodon_reason)

# check for twitter account information
t_account = db.get_twitter_account()
t = TwitterApp(client_id=conf['twitter']['client_id'])
if t_account:
    token = t.refresh_token(t_account[3])
    if token:
        db.update_twitter_account(token, t_account[0])
        logging.info("Authorized twitter account {}".format(t_account[1]))
        valid_twitter = "@" + t_account[1]
        valid_twitter_reason = ""
    else:
        logging.info("Not valid token for account {}".format(t_account[1]))
        valid_twitter = ""
        valid_twitter_reason = "Invalid/Expired token for twitter account"
else:
    logging.info("No twitter account found")
    valid_twitter = ""
    valid_twitter_reason = "No authorized twitter account found"

# start scheduler
scheduler = BackgroundScheduler()
scheduler.start()
# pause if autostart is not enabled
if not conf['app'].get('autostart'):  scheduler.pause()
  
if valid_mastodon and valid_twitter:
    #start xpost job if validated accounts
    xpost_job = scheduler.add_job(xpost,args=[conf,db_file],trigger='interval',minutes=conf['app']['interval'])

@app.route("/", methods=['GET', 'POST'])
def index():
    global twitter
    
    if request.method == 'POST':
        if request.form.get('mastobutton') == 'pause':
            scheduler.pause()
        elif request.form.get('mastobutton') == 'resume':
            scheduler.resume()
        elif request.form.get('mastobutton') == 'authorize':
            twitter = TwitterApp(conf['twitter']['client_id'], client_secret=conf['twitter']['client_secret'],
                                 redirect_uri=conf['twitter']['redirect_uri'], scope=scopes)
            authorization_url, state = twitter.authorization_url() 
            session["oauth_state"] = state
            return redirect(authorization_url)

    if valid_mastodon and valid_twitter:
        if scheduler.state == 1:   #running
            mastobot_state = "Running"
        elif scheduler.state == 2: #paused
            mastobot_state = "Paused"
    else:
        mastobot_state = "Fail"
        
    return render_template('main.html', mastobot_state=mastobot_state,
                                            valid_mastodon=valid_mastodon,
                                            valid_mastodon_reason=valid_mastodon_reason,
                                            valid_twitter=valid_twitter, 
                                            valid_twitter_reason=valid_twitter_reason)
    

@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    token = twitter.fetch_token(code)
    user = twitter.whoami()
    db.insert_twitter_account(user['data']['id'], user['data']['username'], m.userid)
    db.update_twitter_account(token, user['data']['id'])
    global valid_twitter
    global valid_twitter_reason
    valid_twitter = "@" + user['data']['username']
    valid_twitter_reason = ""
    global xpost_job
    xpost_job = scheduler.add_job(xpost,args=[conf,db_file],trigger='interval',minutes=conf['app']['interval'])
    if not conf['app'].get('autostart'):  scheduler.pause()
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0')