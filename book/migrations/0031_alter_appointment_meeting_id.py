# Generated by Django 3.2.4 on 2021-08-17 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0030_remove_appointment_unique_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='meeting_id',
            field=models.CharField(blank=True, default=None, max_length=48, null=True, unique=True),
        ),
    ]
