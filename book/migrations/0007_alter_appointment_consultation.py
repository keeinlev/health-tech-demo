# Generated by Django 3.2 on 2021-05-07 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0006_auto_20210506_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='consultation',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
