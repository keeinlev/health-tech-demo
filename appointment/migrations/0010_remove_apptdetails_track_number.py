# Generated by Django 3.2.4 on 2021-07-07 21:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0009_rename_prescription_apptdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apptdetails',
            name='track_number',
        ),
    ]
