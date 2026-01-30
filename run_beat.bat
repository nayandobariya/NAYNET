@echo off
echo Starting Celery Beat...
celery -A job beat --loglevel=info
pause
