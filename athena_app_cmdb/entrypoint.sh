#!/bin/sh

python manage.py flush --no-input
gunicorn --config /opt/athena_app_cmdb/gunicorn_cfg.py app_registry.wsgi:application
exec "$@"
