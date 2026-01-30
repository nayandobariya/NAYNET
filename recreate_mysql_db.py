import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from django.db import connections

def recreate_mysql_database():
    # Connect to MySQL without specifying a database
    import MySQLdb

    # Get database settings
    db_settings = settings.DATABASES['mysql_db']

    # Connect to MySQL server (not to the specific database)
    conn = MySQLdb.connect(
        host=db_settings['HOST'],
        user=db_settings['USER'],
        passwd=db_settings['PASSWORD'],
        port=int(db_settings['PORT'])
    )
    cursor = conn.cursor()

    # Drop the database if it exists
    db_name = db_settings['NAME']
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
        print(f"Dropped database: {db_name}")
    except Exception as e:
        print(f"Error dropping database {db_name}: {e}")

    # Create the database
    try:
        cursor.execute(f"CREATE DATABASE {db_name};")
        print(f"Created database: {db_name}")
    except Exception as e:
        print(f"Error creating database {db_name}: {e}")

    cursor.close()
    conn.close()

    print("MySQL database recreation complete.")

if __name__ == "__main__":
    recreate_mysql_database()
