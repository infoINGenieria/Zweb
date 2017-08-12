from .local import *

DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': '../zweb.db',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "zweb_test",  #zilleprojects
        'USER': "root",  # ,"root"
        'PASSWORD': "zille123",  # , "zille123"
        "HOST": "127.0.0.1",  # , "127.0.0.1"
        "POST": "3306"
    }
}

CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

MEDIA_ROOT = normpath(join(SITE_ROOT, '../../test_media'))

PRIVATE_STORAGE_CONTAINER = None

