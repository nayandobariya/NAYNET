web: daphne job.asgi:application --port $PORT --bind 0.0.0.0
worker: celery -A job worker --loglevel=info
