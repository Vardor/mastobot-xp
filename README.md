# Mastobot XP

Script para crear un bot auto alojado que permite hacer crossposting desde Mastodon a Twitter.

## Características
* Re publica automáticamente en twitter tus publicaciones de Mastodon. 
* Permite responder o comentar un tweet desde Mastodon
* Permite hacer crossposting de las respuestas a algunos bots de twitter.

## Restricciones
Debido a las restricciones en la API gratuita de Twitter, hay algunas limitacaciones:
* Se puede publicar un máximo de 50 posts diarios y 1500 posts mensuales en Twitter (Más que suficiente para cualquier usuario casual)
* En twitter solo se publica texto. Las imágenes, videos y encuestas no son re-publicadas.

## Requisitos
* Twitter:
  * Una cuenta válida
  * Tokens de la API gratuita (client_id/client_secret)
* Mastodon:
  * Una cuenta válida
  * Un token de aplicación

## Instalación 
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