web: gunicorn flaskapi:app
worker: celery -A task worker -l info -B