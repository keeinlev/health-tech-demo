# Generated by Django 3.2.3 on 2021-06-09 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0025_appointment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='type',
            field=models.BooleanField(blank=True, choices=[(1, 'Video'), (0, 'Phone')], default=None, null=True),
        ),
    ]
