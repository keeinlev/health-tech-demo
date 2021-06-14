# Generated by Django 3.2.3 on 2021-06-11 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0041_auto_20210611_1336'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('email__isnull', True), ('phone__isnull', False)), models.Q(('email__isnull', False), ('phone__isnull', True)), models.Q(('email__isnull', False), ('phone__isnull', False)), _connector='OR'), name='accounts_user_email_or_phone'),
        ),
    ]