# Notes
BUG: RQ doesn't work on windows. Pull request merged but version not released. Worker must be started from linux.
https://github.com/rq/rq/pull/1852

Frontend: http://localhost:$FLASK_PORT/front

# Manuel
## Setup
sh app.setup.sh

## Run
sh app.run.sh

# Docker
docker-compose up -d

# Env
Voir .env et .env.docker

- SET FLASK_APP=app.py
- SET ALLOW_EMPTY_PASSWORD=yes
- SET APPLICATION_REDIS_PORT=6889
- SET APPLICATION_REDIS_URI=redis://localhost
- SET APPLICATION_DATABASE_HOST=localhost
- SET APPLICATION_DATABASE_NAME=api8inf349
- SET APPLICATION_DATABASE_PASSWORD=pass
- SET APPLICATION_DATABASE_PORT=5432
- SET APPLICATION_DATABASE_USER=user
- SET APPLICATION_PRODUCT_SERVICE=http://dimprojetu.uqac.ca/~jgnault/shops/products/
- SET APPLICATION_SHOP_SERVICE=http://dimprojetu.uqac.ca/~jgnault/shops/pay/