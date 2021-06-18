# Generated by Django 3.2.3 on 2021-06-16 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0026_alter_appointment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='time',
            field=models.IntegerField(choices=[(800, '8:00AM'), (815, '8:15AM'), (830, '8:30AM'), (845, '8:45AM'), (900, '9:00AM'), (915, '9:15AM'), (930, '9:30AM'), (945, '9:45AM'), (1000, '10:00AM'), (1015, '10:15AM'), (1030, '10:30AM'), (1045, '10:45AM'), (1100, '11:00AM'), (1115, '11:15AM'), (1130, '11:30AM'), (1145, '11:45AM'), (1200, '12:00PM'), (1215, '12:15PM'), (1230, '12:30PM'), (1245, '12:45PM'), (1300, '1:00PM'), (1315, '1:15PM'), (1330, '1:30PM'), (1345, '1:45PM'), (1400, '2:00PM'), (1415, '2:15PM'), (1430, '2:30PM'), (1445, '2:45PM'), (1500, '3:00PM'), (1515, '3:15PM'), (1530, '3:30PM'), (1545, '3:45PM'), (1600, '4:00PM'), (1615, '4:15PM'), (1630, '4:30PM'), (1645, '4:45PM'), (1700, '5:00PM'), (1715, '5:15PM'), (1730, '5:30PM'), (1745, '5:45PM'), (1800, '6:00PM'), (1815, '6:15PM'), (1830, '6:30PM'), (1845, '6:45PM'), (1900, '7:00PM'), (1915, '7:15PM'), (1930, '7:30PM'), (1945, '7:45PM')], default=None),
        ),
    ]