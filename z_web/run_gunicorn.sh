#!/bin/bash
gunicorn --bind 0.0.0.0:8000 zillepro_web.wsgi --reload -w 2 -e DJANGO_SETTINGS_MODULE='zillepro_web.settings.local'
