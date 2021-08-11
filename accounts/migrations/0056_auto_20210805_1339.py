# Generated by Django 3.2.4 on 2021-08-05 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0055_user_target_new_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorinfo',
            name='email_conf',
            field=models.BooleanField(default=False, verbose_name='Email Confirmed?'),
        ),
        migrations.AddField(
            model_name='doctorinfo',
            name='office_coords',
            field=models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='Doctor Office Coords'),
        ),
        migrations.AlterField(
            model_name='patientinfo',
            name='address_coords',
            field=models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='User Address Coords'),
        ),
    ]