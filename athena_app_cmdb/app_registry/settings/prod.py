
from os import environ
from app_registry.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ["SECRET_KEY"],

DEBUG = False

TEMPLATES[0]['OPTIONS']['debug'] = False

APPEND_SLASH = False

# Cache time to live is 15 minutes.
CACHE_TTL = 60 * 5
