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

