import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from django.db import connections

def reset_mysql_database():
    cursor = connections['mysql_db'].cursor()

    # Drop all tables
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"DROP TABLE {table_name};")
            print(f"Dropped table: {table_name}")
        except Exception as e:
            print(f"Error dropping {table_name}: {e}")

    # Recreate django_migrations table
    cursor.execute("""
        CREATE TABLE django_migrations (
            id int AUTO_INCREMENT NOT NULL PRIMARY KEY,
            app varchar(255) NOT NULL,
            name varchar(255) NOT NULL,
            applied datetime(6) NOT NULL
        );
    """)
    print("Recreated django_migrations table.")

    print("MySQL database reset complete.")

if __name__ == "__main__":
    reset_mysql_database()
    # Now run migrate
    execute_from_command_line(['manage.py', 'migrate', '--database=mysql_db'])
