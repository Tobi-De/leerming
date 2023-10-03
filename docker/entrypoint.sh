#!/bin/sh

python manage.py compress
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py makesuperuser
#gunicorn config.wsgi --config="docker/gunicorn.conf.py"
granian --interface asgi config.asgi:application --host 0.0.0.0 --port 80 --workers 4