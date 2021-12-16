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

AMIDCREDENTIALS = {
    'username': 'asset-user',
    'password': '1tsrAIn1NGcts&DGS!'
    }
AMIDURL = 'http://api-int.connectcdk.com/api/ari-assets-backend/v1/api/ari-assets-backend/v1'


##### AUTH LDAP STUFF HERE  ################################################
#
#
#
AUTH_LDAP_SERVER_URI = os.getenv('AUTH_LDAP_SERVER_URI', "ldap://global.cdk.com:389")
AUTH_LDAP_BIND_DN = os.getenv('AUTH_LDAP_BIND_DN', "CN=svc_athena_devops,OU=Service Accounts,OU=LDAP,OU=Security,OU=GIS,DC=global,DC=cdk,DC=com")
AUTH_LDAP_BIND_PASSWORD = os.getenv('AUTH_LDAP_BIND_PASSWORD', os.getenv('bamboo_password'))
# AUTH_LDAP_USER_SEARCH = LDAPSearch(
#     "ou=People,dc=local,dc=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
# )
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    #os.getenv('AUTH_LDAP_USER_SEARCH', "ou=People,dc=local,dc=com"),
    os.getenv('AUTH_LDAP_USER_SEARCH', "ou=Enabled Users,ou=User Accounts,dc=global,dc=cdk,dc=com"),
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
# AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=django,ou=groups,dc=example,dc=com"

#########Set this later
#AUTH_LDAP_REQUIRE_GROUP = os.getenv('AUTH_LDAP_REQUIRE_GROUP', "cn=msvxeng,ou=Group,dc=local,dc=com")



# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
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


AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
    #"django_auth_ldap.backend.LDAPBackend",

    # comment above and replace with this one to save LDAP last password to django so users can log in with
    #  their last ldap password when ldap is down
    
]

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
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ),
}
