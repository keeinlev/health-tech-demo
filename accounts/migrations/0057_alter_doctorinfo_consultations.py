# Generated by Django 3.2.4 on 2021-08-05 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0056_auto_20210805_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorinfo',
            name='consultations',
            field=models.TextField(default='None', verbose_name="Doctor's Applicable Consultations"),
        ),
    ]