# Mastobot XP

Script para crear un bot auto alojado que permite hacer crossposting desde Mastodon a Twitter.

## Características
* Publica automáticamente en twitter tus posts (toots) de Mastodon. 
* Permite responder o comentar un tweet desde Mastodon
* Permite hacer crossposting de las respuestas a algunos bots de twitter.
* Provee una (muy simple) interfaz web para visualizar el estado.

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
**Utilizando docker**
1. Clonar el repositorio
  `git clone https://git.disroot.org/carloshr/mastobot.git`

2. Copiar el archivo de configuración
  `cp config.sample.yml config.yml`

3. Editar la configuración con tus parámetros
  `vi config.yml`

4. Contruir la imagen
  `docker compose build`

5. Iniciar el contenedor
  `docker compose up -d`

## Opciones del archivo de configuración
### Sección "Mastodon"
- **instance**: (Obligatorio) instancia de mastodon donde está tu cuenta 
- **token**: (Obligatorio) Token de la app de mastodon
### Sección "Twitter"
- **client_id**: (Obligatorio)
- **client_secret**: (Obligatorio)
- **redirect_uri**: (Obligatorio) url local para redireccionar autorización de la cuenta de twitter. Debe estar autorizada en la API.
### Sección "App"
- **max_statuses**: (Obligatorio) Cantidad máxima de toots a publicar en twitter en cada interación.
- **interval**: (required) Invervalo en minutos en que el script chequea si existen nuevas publicaciones.
- **noxp**: (optional) Lista con etiquetas (hashtags) para indicar que un toot no se publique en twitter. Debe estar entre comillas simples y comenzar con #
- **xp_replies**: (opcional)  
- **autostart**: (opcional) Indica si se iniciar automáticamente el crossposting o debe ser iniciado manualmente en la interfaz web.