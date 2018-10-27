"""
Django settings for zillepro_web project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from os.path import abspath, basename, dirname, join, normpath
from sys import path

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/admin/'

# Application definition

INSTALLED_APPS = (
    'frontend',
    'suit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'djangobower',
    'pipeline',
    'bootstrap3',
    'compressor',
    'djangoformsetjs',
    'django_tables2',
    'django_filters',
    'crispy_forms',
    'rest_framework',

    'presupuestos',
    'core',
    'indumentaria',
    'parametros',
    'registro',
    'documento',
    'costos',
    'organizacion',
    'zweb_utils',
    'reportes',
    'api',
    'proyecciones',
    'equipos',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DATE_FORMAT': '%d/%m/%Y',
    'DATETIME_FORMAT': '%d/%m/%Y %H:%M:%S',
    'DATE_INPUT_FORMATS': ['%d/%m/%Y', 'iso-8601'],
    'DATETIME_INPUT_FORMATS': ['%d/%m/%Y %H:%M:%S', 'iso-8601'],
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PARSER_CLASSES': ('rest_framework.parsers.JSONParser', ),
    'PAGE_SIZE': 50,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

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

STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'ng-zille', 'dist')),
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
MEDIA_ROOT = normpath(join(SITE_ROOT, '../media'))
STATIC_ROOT = normpath(join(SITE_ROOT, '../collected_static'))

BOWER_COMPONENTS_ROOT = normpath(join(SITE_ROOT, '../components'))
PIPELINE_SASS_ARGUMENTS = "-p 8 -I '%s' -I '%s'" % (
         join(BOWER_COMPONENTS_ROOT, 'bower_components/bootstrap-sass/assets/stylesheets/'),
         join(BOWER_COMPONENTS_ROOT, 'bower_components/bootstrap-sass/assets/fonts/')
)

PIPELINE = {
    'PIPELINE_ENABLED': False,
    'STORAGE': STATICFILES_STORAGE,
    'STYLESHEETS': {
        'base': {
            'source_filenames': (
                'bootstrap-sass/assets/stylesheets/_bootstrap.scss',
                'bootstrap3-dialog/dist/css/bootstrap-dialog.css',
                'font-awesome/css/font-awesome.min.css',
                'frontend/css/theme.bootstrap.min.css',
                'datatables.net-bs/css/dataTables.bootstrap.css',
                'bootstrap-datepicker/dist/css/bootstrap-datepicker3.css',
                'frontend/css/base.scss',
                'chosen/chosen.min.css',
                'animate.css/animate.min.css',
            ),
            'output_filename': 'css/base.css',
            'extra_context': {
                'media': 'screen,projection',
            },
        },
        'base_admin': {
            'source_filenames': (
                'chosen/chosen.min.css',
                'frontend/css/base_admin.scss',
            ),
            'output_filename': 'css/base_admin.css',
            'extra_context': {
                'media': 'screen,projection',
            }
        },
        'plugins': {
            'source_filenames': (
                'datatables/media/css/jquery.dataTables.css',
                'datatables/media/css/dataTables.bootstrap.css',
            ),
            'output_filename': 'css/plugin.css',
        }
    },
    'JAVASCRIPT': {
        'base_js': {
            'source_filenames': (
                'jquery/dist/jquery.js',
                'bootstrap-sass/assets/javascripts/bootstrap.js',
                'bootstrap3-dialog/dist/js/bootstrap-dialog.js',
                'chosen/chosen.jquery.min.js',
                'jquery-form/jquery.form.js',
            ),
            'output_filename': 'js/base_js.js',
        },
        'plugins_js': {
            'source_filenames': (
                'datatables/media/js/jquery.dataTables.js',
                'datatables/media/js/dataTables.bootstrap.js',
                'bootstrap-datepicker/dist/js/bootstrap-datepicker.js',
                'bootstrap-datepicker/dist/locales/bootstrap-datepicker.es.min.js',
                'PACE/pace.js',

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
        },
        'zweb_utils_js': {
            'source_filenames': (
                'frontend/js/zweb_utils.js',
            ),
            'output_filename': 'js/zweb_utils.js',
        },
    },
    'COMPILERS': (
        'pipeline.compilers.sass.SASSCompiler',
    ),
    'SASS_BINARY': 'sassc',
    'CSS_COMPRESSOR': None,
    'JS_COMPRESSOR': None,
    'SASS_ARGUMENTS': PIPELINE_SASS_ARGUMENTS
}

# django-compressor settings
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

BOWER_INSTALLED_APPS = (
    'jquery#2.1',
    'd3#3.3.13',
    'nvd3#1.7.1',
    'bootstrap-sass#3.3',
    'fontawesome#4.7',
    'datatables#~1.10.10',
    'bootstrap3-dialog#1.34.9',
    'chosen#1.4.2',
    'pace#1.0.2',
    'bootstrap-datepicker#^1.5.1',
    'jquery-form#3.46.0',
    'animate.css#^3.5.2'
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
                'django.core.context_processors.request',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'frontend.context_processors.user_menu'
            ],
        },
    },
]

WSGI_APPLICATION = 'zillepro_web.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Argentina/Mendoza'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (normpath(join(DJANGO_ROOT, 'locale')), )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

WEASYPRINT_BASEURL = ''

SUIT_CONFIG = {
    'ADMIN_NAME': 'ZILLE - Administración',
    'HEADER_DATE_FORMAT': 'l, d F Y',
    'SEARCH_URL': 'admin:core_operarios_changelist',
    'MENU': (
        'core', 'organizacion', 'costos', 'documento', 'parametros',
        'registro', 'equipos',
        {'app': 'auth', 'label': 'Usuarios', 'icon': 'icon-user'},
        {'label': 'Volver a la aplicación', 'url': 'index', 'icon': 'icon-th'},
    )
}

# Default settings
BOOTSTRAP3 = {
     # Label class to use in horizontal forms
    'horizontal_label_class': 'col-sm-2',

    # Field class to use in horizontal forms
    'horizontal_field_class': 'col-sm-10',
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'
