# Mastobot XP

Script to create a self-hosted bot that allows crossposting from Mastodon to Twitter.

(Instructions in spanish [here](README.es.md))

## Features

- Automatically posts your Mastodon posts (toots) to Twitter.
- Allows replying or commenting on a tweet directly from Mastodon.
- Enables crossposting of replies to some bots that replicate Twitter accounts.
- Provides a (very simple) web interface to view the status.

## Restrictions

Due to limitations in Twitter's free API, there are some restrictions:

- A maximum of 17 posts per day and 500 posts per month can be published on Twitter (more than enough for any casual user).
- Only text is published on Twitter. Images, videos, and polls are not reposted.

## Requirements

### Twitter:
- A valid account.
- Free API tokens (`client_id`/`client_secret`).

### Mastodon:
- A valid account.
- An application token.

## Installation

### Using Docker

1. Clone the repository:  
   `git clone https://git.disroot.org/carloshr/mastobot.git`  
2. Copy the configuration file:  
   `cp config.sample.yml config.yml`  
3. Edit the configuration with your parameters:  
   `vi config.yml`  
4. Build the Docker image:  
   `docker compose build`  
5. Start the container:  
   `docker compose up -d`  

## Configuration File Options

### Mastodon Section

- `instance`: (Required) Mastodon instance where your account is located.
- `token`: (Required) Mastodon app token.

### Twitter Section

- `client_id`: (Required)
- `client_secret`: (Required)
- `redirect_uri`: (Required) Local URL for redirecting Twitter account authorization. Must be authorized in the API.

### App Section

- `max_statuses`: (Required) Maximum number of toots to publish on Twitter per interaction.
- `interval`: (Required) Interval in minutes for the script to check for new posts.
- `noxp`: (Optional) List of hashtags to indicate that a toot should not be published on Twitter. Must be in single quotes and start with `#`.
- `xp_replies`: (Optional) Replicated Twitter bot accounts for which you want to enable crossposting. (The bot must publish a link to the original tweet).
- `autostart`: (Optional) Indicates whether crossposting should start automatically or be manually started via the web interface.