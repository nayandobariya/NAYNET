@echo off
echo Starting Celery Worker...
echo Make sure Redis is running (redis-server).
celery -A job worker --loglevel=info -P solo
pause
