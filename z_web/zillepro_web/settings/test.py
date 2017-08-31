import logging
from .local import *

DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG
logging.disable(logging.CRITICAL)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '../zweb.db',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': "zweb_test",  #zilleprojects
#         'USER': "root",  # ,"root"
#         'PASSWORD': "zille123",  # , "zille123"
#         "HOST": "127.0.0.1",  # , "127.0.0.1"
#         "POST": "3306"
#     }
# }

CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

MEDIA_ROOT = normpath(join(SITE_ROOT, '../../test_media'))

PIPELINE['PIPELINE_ENABLED'] = True

class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


MIGRATION_MODULES = DisableMigrations()

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# speed up tests
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
