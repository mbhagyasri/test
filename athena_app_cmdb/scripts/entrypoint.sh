#!/bin/sh

python manage.py makemigrations --no-input --merge
python manage.py migrate --no-input
gunicorn --config /opt/athena_app_cmdb/gunicorn_cfg.py app_registry.wsgi:application

exec "$@"
