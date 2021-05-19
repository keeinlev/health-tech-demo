# Generated by Django 3.2 on 2021-05-05 02:43

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientinfo',
            name='ohip_expiry',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='OHIP Expiry Date'),
        ),
        migrations.AlterField(
            model_name='patientinfo',
            name='ohip_number',
            field=models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(code='nomatch', message='Length must be 12', regex='^{12}$')], verbose_name='OHIP Number'),
        ),
    ]
