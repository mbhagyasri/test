from app_registry.settings.base import *
import os
import json

DEBUG = True


TEMPLATES[0]['OPTIONS']['debug'] = True

APPEND_SLASH = False

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Cache time to live is 1s
CACHE_TTL = 1

DEFAULT_DB_CONFIG = '{"endpoint": "postgres:5432", "username": "postgres", "password": "postgres"}'
DB_CONFIG = json.loads(os.getenv('DB_CONFIG', DEFAULT_DB_CONFIG))
DB_HOST = "postgres"
DB_PORT = "5432"
if 'endpoint' in DB_CONFIG and DB_CONFIG.get('endpoint', "") != "":
    array = DB_CONFIG.get('endpoint').split(':')
    DB_HOST = array[0]
    DB_PORT = array[1]
DATABASES = {
    'default': {
        'ENGINE': os.getenv('SQL_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('SQL_DATABASE', 'postgres'),
        'USER': DB_CONFIG.get('username', 'postgres'),
        'PASSWORD': DB_CONFIG.get('password', 'password'),
        'HOST': DB_HOST,
        'PORT': DB_PORT
    }
}