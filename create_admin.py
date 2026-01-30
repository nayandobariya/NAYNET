import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser('admin@example.com', 'admin123')
    print('Superuser created: email=admin@example.com, password=admin123')
else:
    print('Superuser already exists')
