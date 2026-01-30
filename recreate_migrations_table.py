import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from django.db import connections

# Recreate the django_migrations table if it doesn't exist
cursor = connections['mysql_db'].cursor()

# Check if django_migrations table exists
cursor.execute("SHOW TABLES LIKE 'django_migrations';")
if not cursor.fetchone():
    # Create the django_migrations table
    cursor.execute("""
        CREATE TABLE django_migrations (
            id int AUTO_INCREMENT NOT NULL PRIMARY KEY,
            app varchar(255) NOT NULL,
            name varchar(255) NOT NULL,
            applied datetime(6) NOT NULL
        );
    """)
    print("Created django_migrations table.")
else:
    print("django_migrations table already exists.")

# Clear all migration records
cursor.execute("DELETE FROM django_migrations;")
print("Cleared all migration records.")
