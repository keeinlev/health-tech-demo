# Generated by Django 3.2.4 on 2021-07-22 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0029_appointment_unique_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='unique_id',
        ),
    ]