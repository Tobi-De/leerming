#!/bin/sh

python manage.py compress
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py installwatson
python manage.py makesuperuser
#gunicorn config.wsgi --config="docker/gunicorn.conf.py"
granian --interface wsgi config.wsgi:application --host 0.0.0.0 --port 80 --workers 4
