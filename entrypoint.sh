#!/bin/bash
python manage.py migrate
exec gunicorn finSentiments.wsgi:application --bind 0.0.0.0:8000 --workers=1 --threads=1