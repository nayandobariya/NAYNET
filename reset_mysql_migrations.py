import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from django.db import connections

# Delete all migration records for MySQL database
cursor = connections['mysql_db'].cursor()
cursor.execute("DELETE FROM django_migrations;")
print("Deleted all migration records from MySQL database.")
