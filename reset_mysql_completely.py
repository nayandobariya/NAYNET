import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from django.db import connections

def reset_mysql_completely():
    cursor = connections['mysql_db'].cursor()

    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    # Get all table names
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in database.")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        return

    # Convert to list of table names
    table_names = [table[0] for table in tables]
    print(f"Found tables: {table_names}")

    # Drop all tables
    for table_name in table_names:
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

    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    print("MySQL database reset complete.")

if __name__ == "__main__":
    reset_mysql_completely()
