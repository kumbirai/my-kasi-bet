#!/bin/bash
# Bootstrap Let's Encrypt certificates for srv1498298.hstgr.cloud
# Run once on the server before starting the full stack.

set -e

DOMAIN="srv1498298.hstgr.cloud"
EMAIL="kumbirai@gmail.com"
STAGING=0   # Set to 1 to test against LE staging (avoids rate limits)

CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
RSA_KEY_SIZE=4096
DATA_PATH="$(dirname "$0")/../"   # project root (where docker-compose.yml lives)

cd "$DATA_PATH"

if [ -d "$CERT_PATH" ]; then
  echo "Certificates already exist for $DOMAIN — skipping."
  echo "To force renewal run: docker compose run --rm certbot renew --force-renewal"
  exit 0
fi

echo "### Creating dummy certificate for $DOMAIN ..."
docker compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$RSA_KEY_SIZE -days 1 \
    -keyout '$CERT_PATH/privkey.pem' \
    -out '$CERT_PATH/fullchain.pem' \
    -subj '/CN=localhost'" certbot

echo "### Starting nginx with dummy certificate ..."
docker compose up --force-recreate -d nginx

echo "### Removing dummy certificate ..."
docker compose run --rm --entrypoint "\
  rm -rf /etc/letsencrypt/live/$DOMAIN && \
  rm -rf /etc/letsencrypt/archive/$DOMAIN && \
  rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot

STAGING_FLAG=""
if [ "$STAGING" = "1" ]; then
  STAGING_FLAG="--staging"
fi

echo "### Requesting Let's Encrypt certificate for $DOMAIN ..."
docker compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $STAGING_FLAG \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN" certbot

echo "### Reloading nginx ..."
docker compose exec nginx nginx -s reload

echo "### Done. Certificate issued for $DOMAIN."
