# Generated by Django 3.2.3 on 2021-06-09 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0024_appointment_meeting_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='type',
            field=models.CharField(blank=True, choices=[('VIDEO', 'Video'), ('PHONE', 'phone')], default=None, max_length=5, null=True),
        ),
    ]
