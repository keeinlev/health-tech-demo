# Generated by Django 3.2 on 2021-05-07 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_appointment_booked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='datetime',
        ),
        migrations.AddField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='appointment',
            name='time',
            field=models.TimeField(default=None),
        ),
    ]
