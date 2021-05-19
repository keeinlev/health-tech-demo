# Generated by Django 3.2 on 2021-05-05 20:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('consultation', models.CharField(max_length=100)),
                ('doctor', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_doctor', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_patient', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
