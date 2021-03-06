# Generated by Django 3.2.3 on 2021-06-10 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0034_remove_doctorinfo_meeting_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctorinfo',
            name='ms_authenticated',
        ),
        migrations.AddField(
            model_name='user',
            name='ms_authenticated',
            field=models.BooleanField(default=False, verbose_name='Connected to MS Account'),
        ),
    ]
