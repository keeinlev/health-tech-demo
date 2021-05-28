# Generated by Django 3.2.3 on 2021-05-21 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_doctorinfo_meeting_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorinfo',
            name='meeting_url',
            field=models.CharField(default=None, max_length=200, null=True, verbose_name="Doctor's Meeting Link"),
        ),
    ]