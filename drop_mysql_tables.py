import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from django.db import connections

# Drop all tables in MySQL database
cursor = connections['mysql_db'].cursor()

# Get all table names
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

# Drop each table
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"DROP TABLE {table_name};")
        print(f"Dropped table: {table_name}")
    except Exception as e:
        print(f"Error dropping {table_name}: {e}")

print("All tables dropped from MySQL database.")
