# Mastobot XP

A personal selfhosted crossposter from Mastodon to Twitter. Your mastodon posts are mirrored to your twitter account and you can also reply or quote tweets directly from your Mastodon account.

## Features 
* Automatically crosspost from Mastodon to Twitter and adds a link to the original post.
* Can reply a tweet from Mastodon 
* Can quote a tweer from Mastodon

## Restrictions
Due to free Twitter API restrictions there are some restrictions
* Can only post 50 tweets per day and 1500 monthly
* Only text is crossposted. Not images/videos nor any other media.

## Requirement
* Twitter:
  * A valid Twitter account
  * A free twitter API tokens (client_id/client_secret)
* Mastodon:
  * A valid Mastodon Account
  * An app token

## Install
1.  clone repo
  `git clone https://git.disroot.org/carloshr/mastobot.git`

2. Copy config file
  `cp config.sample.yml config.yml`

3. Edit config file with your info 
  `vi config.yml`

4. Build docker image 
  `docker compose build`

5. Start container
  `docker compose up -d`

## Config File Parameters
### Mastodon section
- **instance**: (required) mastodon instance of your account 
- **token**: (required) mastodon app token. It is a string 
### Twitter section
- **client_id**: (required)
- **client_secret**: (required)
- **redirect_uri**: (required)
### App section:
- **max_statuses**: (required)
- **interval**: (required)
- **noxp**: (optional)
- **xp_replies**: (optional)
- **autostart**: (optional)