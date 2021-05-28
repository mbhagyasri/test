#!/bin/sh

python manage.py flush --no-input
python manage.py makemigrations athena_app_cmdb
python manage.py migrate
gunicorn --config /opt/athena_app_cmdb/gunicorn_cfg.py app_registry.wsgi:application

exec "$@"
