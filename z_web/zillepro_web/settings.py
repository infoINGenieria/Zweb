"""
Django settings for zillepro_web project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'frontend',

    'jet.dashboard',
    'jet',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'debug_toolbar',

    'djangobower',
    'pipeline',
    'bootstrap3',
    'compressor',
    'formtools',

    'core',
    'indumentaria',
    'documento',
    'parametros',
    'registro',
    'costos',
    'zweb_utils',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
     'pipeline.finders.PipelineFinder',
     'compressor.finders.CompressorFinder',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, '../media/')
STATIC_ROOT = os.path.join(BASE_DIR, '../collected_static/')
BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, '../components/')
PIPELINE_SASS_ARGUMENTS = "-p 8 -I '%s' -I '%s'" % (
         os.path.join(BOWER_COMPONENTS_ROOT, 'bower_components/bootstrap-sass/assets/stylesheets/'),
         os.path.join(BOWER_COMPONENTS_ROOT, 'bower_components/bootstrap-sass/assets/fonts/')
)

PIPELINE_CSS = {
    'base': {
        'source_filenames': (
            'frontend/css/zweb.scss',
            'font-awesome/css/font-awesome.min.css',
        ),
        'output_filename': 'css/base.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'plugins': {
        'source_filenames': (
            'datatables/media/css/jquery.dataTables.css',
            'datatables/media/css/dataTables.bootstrap.css',
        ),
        'output_filename': 'css/plugin.css',
    }
}

PIPELINE_JS = {
    'base_js': {
        'source_filenames': (
            'jquery/dist/jquery.js',
            'bootstrap-sass/assets/javascripts/bootstrap.js',
        ),
        'output_filename': 'js/base_js.js',
    },
    'plugins_js': {
        'source_filenames': (
            'datatables/media/js/jquery.dataTables.js',
            'datatables/media/js/dataTables.bootstrap.js',
        ),
        'output_filename': 'js/plugins.js',
    },
    'graphics_js': {
        'source_filenames': (
            "d3/d3.min.js",
            "nvd3/build/nv.d3.min.js",
            'frontend/js/graphics.js',
        ),
        'output_filename': 'js/zille.graphics.js',
    }
}

PIPELINE_COMPILERS = (
    'pipeline.compilers.sass.SASSCompiler',
)
PIPELINE_SASS_BINARY = 'sassc'
PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None

# django-compressor settings
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)


BOWER_INSTALLED_APPS = (
    'd3#3.3.13',
    'nvd3#1.7.1',
    'bootstrap-sass#3.3',
    'fontawesome#4.3',
    'datatables#~1.10.10',
)

ROOT_URLCONF = 'zillepro_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'zillepro_web.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Mendoza'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (os.path.join(PROJECT_DIR, 'locale'), )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

JET_DEFAULT_THEME = 'default'

JET_THEMES = [
    {
        'theme': 'default',
        'color': '#47bac1',
        'title': 'Default'
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Verde'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Azul Claro'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Gris Claro'
    }
]

try:  # import the local settings
    from .settings_local import *  # noqa
except ImportError:
    print('You need to define a settings_local.py')
    exit()
