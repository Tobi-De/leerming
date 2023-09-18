python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000
# fastwsgi config.wsgi:application --host 0.0.0.0 --port 8000