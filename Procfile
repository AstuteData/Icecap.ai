web: gunicorn flaskapi:app
worker: celery -A tasks worker -l info --concurrency 2