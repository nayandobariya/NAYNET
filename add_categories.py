import os
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

from jobapp.models import Category

# List of categories to add
categories = [
    'Technology',
    'Marketing',
    'Finance',
    'Healthcare',
    'Education',
    'Engineering',
    'Sales',
    'Human Resources',
    'Design',
    'Operations',
    'Black Place'  # Keeping the existing one
]

created_count = 0
for category_name in categories:
    category, created = Category.objects.get_or_create(name=category_name)
    if created:
        created_count += 1
        print(f"Created category: {category_name}")
    else:
        print(f"Category already exists: {category_name}")

print(f"\nTotal categories created: {created_count}")
print(f"Total categories in database: {Category.objects.count()}")
