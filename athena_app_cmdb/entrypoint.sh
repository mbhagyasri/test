#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py makemigrations athena_app_cmdb
python manage.py migrate
python manage.py collectstatic --no-input --ignore=.scss
gunicorn --config /opt/athena_app_cmdb/gunicorn_cfg.py AppRegistry.wsgi:application
exec "$@"
