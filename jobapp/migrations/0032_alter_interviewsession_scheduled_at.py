# Generated manually to make scheduled_at nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0031_auto_20260116_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewsession',
            name='scheduled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
