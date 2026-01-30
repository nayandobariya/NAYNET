import os
import django
from django.core.files import File
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job.settings')
django.setup()

# Set mysql_db as the default database for this script
connections.databases['default'] = connections.databases['mysql_db']

from django.contrib.auth import get_user_model
from jobapp.models import Category, Job, Applicant, BookmarkJob
from account.models import CV
import random

User = get_user_model()

# Sample data
categories = ['Technology', 'Marketing', 'Finance', 'Healthcare', 'Education']
locations = ['New York', 'San Francisco', 'London', 'Berlin', 'Tokyo']
companies = ['TechCorp', 'MarketInc', 'FinanceLtd', 'HealthCare', 'EduWorld']

# Create categories
for cat in categories:
    Category.objects.using('mysql_db').get_or_create(name=cat)

# Create employers
employers = []
for i in range(5):
    email = f'employer{i}@example.com'
    user, created = User.objects.using('mysql_db').get_or_create(
        email=email,
        defaults={
            'first_name': f'Employer{i}',
            'last_name': 'User',
            'role': 'employer',
            'gender': 'M' if i % 2 == 0 else 'F'
        }
    )
    if created:
        user.set_password('password123')
        user.save()
    employers.append(user)

# Create employees
employees = []
for i in range(10):
    email = f'employee{i}@example.com'
    user, created = User.objects.using('mysql_db').get_or_create(
        email=email,
        defaults={
            'first_name': f'Employee{i}',
            'last_name': 'User',
            'role': 'employee',
            'gender': 'F' if i % 2 == 0 else 'M'
        }
    )
    if created:
        user.set_password('password123')
        user.save()
    employees.append(user)

# Create jobs
jobs = []
for i in range(20):
    employer = random.choice(employers)
    category = random.choice(Category.objects.using('mysql_db').all())
    job = Job.objects.using('mysql_db').create(
        user=employer,
        title=f'Software Developer {i}',
        description=f'Job description for position {i}. Requires skills in Python, Django, etc.',
        location=random.choice(locations),
        job_type=str(random.randint(1, 3)),
        category=category,
        salary=f'${random.randint(50000, 150000)}',
        company_name=random.choice(companies),
        company_description=f'Company description {i}',
        url=f'https://example{i}.com',
        last_date=f'2024-12-{random.randint(1, 31)}',
        is_published=True
    )
    jobs.append(job)

# Create applicants
for i in range(50):
    employee = random.choice(employees)
    job = random.choice(jobs)
    Applicant.objects.using('mysql_db').get_or_create(
        user=employee,
        job=job
    )

print('Sample data populated successfully!')
