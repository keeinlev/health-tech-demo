# Generated by Django 3.2 on 2021-05-19 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0022_appointment_prescription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='prescription',
        ),
    ]
