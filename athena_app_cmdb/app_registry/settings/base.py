"""
Django settings for app_registry project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import mimetypes
import ldap
import json
import athena_app_cmdb as project_module
from collections import OrderedDict
from django_auth_ldap.config import LDAPSearch, PosixGroupType
from datetime import timedelta


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.realpath(project_module.__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/


ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'bootstrap4',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'bootstrap_modal_forms',
    'widget_tweaks',
    'athena_app_cmdb',
    'django_json_widget',
    'django_extensions',
    'admin_auto_filters',
    'auditlog'

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'request_logging.middleware.LoggingMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
    'athena_app_cmdb.middleware.ViewExceptionMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

ROOT_URLCONF = 'app_registry.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, '../athena_app_cmdb/templates'),
                 os.path.join(PROJECT_DIR, '../athena_app_cmdb/templates/athena_app_cmdb')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "django.template.context_processors.request",
                "django.template.context_processors.static",
            ],
        },
    },
]


WSGI_APPLICATION = 'app_registry.wsgi.application'

SECRET_KEY = os.getenv('SECRET_KEY')


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DEFAULT_DB_CONFIG = '{"endpoint": "postgres:5432", "username": "postgres", "password": "postgres"}'
DB_CONFIG = json.loads(os.getenv('DB_CONFIG', DEFAULT_DB_CONFIG))
DB_HOST = "postgres"
DB_PORT = "5432"
if 'endpoint' in DB_CONFIG and DB_CONFIG.get('endpoint', "") != "":
    array = DB_CONFIG.get('endpoint').split(':')
    DB_HOST = array[0]
    DB_PORT = array[1]
ssl_options = {'sslmode': os.getenv('PG_SSL_MODE', 'verify-full'),
                    'sslrootcert': os.path.join(PROJECT_DIR, '../etc/rds-combined-ca-bundle.pem'),
                    'ssl_min_protocol_version': 'TLSv1.2'}
if os.getenv('env_type', '') == 'local':
    ssl_options = {}

DATABASES = {
    'default': {
        'ENGINE': os.getenv('SQL_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('SQL_DATABASE', 'postgres'),
        'USER': DB_CONFIG.get('username', 'postgres'),
        'PASSWORD': DB_CONFIG.get('password', 'password'),
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': ssl_options
    }
}
DEFAULT_REDIS_CONFIG = '{"endpoint": "", "username": "", "password": ""}'
REDIS_CONFIG = json.loads(os.getenv('REDIS_CONFIG', DEFAULT_REDIS_CONFIG))
REDIS_HOST = "redis"
REDIS_PORT = "6379"
if 'endpoint' in REDIS_CONFIG and REDIS_CONFIG.get('endpoint', "") != "":
    array = REDIS_CONFIG.get('endpoint').split(':')
    REDIS_HOST = array[0]
    REDIS_PORT = array[1]
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/0".format(REDIS_HOST, REDIS_PORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        'TIMEOUT': 60
    }
}


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 30 * 60

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


REST_FRAMEWORK = {
    'PAGE_SIZE': 2000,
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_PAGINATION_CLASS': 'athena_app_cmdb.paginator.Pagination',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    # The default set of renderers may be set globally, using the DEFAULT_RENDERER_CLASSES setting.
    # For example, the following settings would use JSON as the main media type and also include the self describing
    # API.
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS512',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('JWT',),

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}

AUTH_LDAP_SERVER_URI = os.getenv('AUTH_LDAP_SERVER_URI', "ldap://127.0.0.1")
AUTH_LDAP_BIND_DN = os.getenv('AUTH_LDAP_BIND_DN', "cn=ldapadm,dc=local,dc=com")
AUTH_LDAP_BIND_PASSWORD = os.getenv('AUTH_LDAP_BIND_PASSWORD', "")
# AUTH_LDAP_USER_SEARCH = LDAPSearch(
#     "ou=People,dc=local,dc=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
# )
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.getenv('AUTH_LDAP_USER_SEARCH', "ou=People,dc=local,dc=com"),
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)
# Or:
# AUTH_LDAP_USER_DN_TEMPLATE = 'uid=%(user)s,ou=People,dc=local,dc=com'

# Set up the basic group parameters.
# AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
#     "ou=Group,dc=local,dc=com",
#     ldap.SCOPE_SUBTREE,
#     "(objectClass=posixGroup)",
# )
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    os.getenv('AUTH_LDAP_GROUP_SEARCH', "ou=Group,dc=local,dc=com"),
    ldap.SCOPE_SUBTREE,
    "(objectClass=posixGroup)",
)
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

# Simple group restrictions
# AUTH_LDAP_REQUIRE_GROUP = "cn=msvxeng,ou=Group,dc=local,dc=com"
AUTH_LDAP_REQUIRE_GROUP = os.getenv('AUTH_LDAP_REQUIRE_GROUP', "cn=msvxeng,ou=Group,dc=local,dc=com")
# AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=django,ou=groups,dc=example,dc=com"

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "sn",
    "last_name": "sn",
    "email": "mail",
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_active": "cn=active,ou=ou=Group,dc=local,dc=com",
     "is_staff": os.getenv('AUTH_LDAP_REQUIRE_GROUP', "cn=athenaDevelopersAdmins,ou=Group,dc=local,dc=com"),
     "is_superuser": os.getenv('AUTH_LDAP_REQUIRE_GROUP', "cn=athenaDevelopersAdmins,ou=Group,dc=local,dc=com"),
}

# This is the default.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = False

# Cache distinguished names and group memberships for an hour to minimize
# LDAP traffic.
AUTH_LDAP_CACHE_TIMEOUT = 3600

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    #"django_auth_ldap.backend.LDAPBackend",

    # comment above and replace with this one to save LDAP last password to django so users can log in with
    #  their last ldap password when ldap is down
    "athena_app_cmdb.utils.backends.LDAPBackend",
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, '../athena_app_cmdb/static')
]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, '../static')

mimetypes.add_type("text/css", ".css", True)

SESSION_EXPIRE_SECONDS = 86400  # 1 day
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = 60  # group by minute
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
CACHE_TTL = 5

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'class': 'jsonformatter.JsonFormatter',
            'format': OrderedDict([
                ("ts", "%(asctime)s"),
                ("FunctionName", "%(funcName)s"),
                ("loglevel", "%(levelname)s"),
                ("source", '%(pathname)s:%(lineno)d'),
                ("message", "%(message)s"),
            ])
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'json_console': {
            'level': 'INFO',
            'formatter': 'json',
            'class': 'logging.StreamHandler'
        },
        'debug_console': {
          'level': 'DEBUG',
          'filters': ['require_debug_true'],
          'class': 'logging.StreamHandler',
          'formatter': 'json'
        }
    },
    'root': {
        'handlers': ['json_console', 'debug_console'],
        'level': 'INFO'
    },
    'loggers': {
        'django': {
            'handlers': ['json_console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['json_console'],
            'level': 'ERROR',
            'propagate': False
        },

    }
}

AMIDCREDENTIALS = {
    'username': 'asset-user',
    'password': '1tsrAIn1NGcts&DGS!'
    }

AMIDURL = 'http://api-int.connectcdk.com/api/ari-assets-backend/v1/api/ari-assets-backend/v1'