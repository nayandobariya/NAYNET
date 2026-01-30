from account.models import User
from jobapp.models import Job

print(f'Employees: {User.objects.filter(role="employee").count()}')
print(f'Employers: {User.objects.filter(role="employer").count()}')
print(f'Published Jobs: {Job.objects.filter(is_published=True).count()}')
print(f'Closed Jobs: {Job.objects.filter(is_closed=True).count()}')
