import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from django.db import connections

# Check MySQL database tables
cursor = connections['mysql_db'].cursor()
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()
print("Tables in MySQL database 'naynat':")
for table in tables:
    print(table[0])
