# Generated by Django 4.2.1 on 2023-05-09 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasycalendar', '0002_alter_timeunit_base_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeunit',
            name='base_unit_instance_names',
            field=models.CharField(default='', max_length=800),
        ),
        migrations.AlterField(
            model_name='timeunit',
            name='time_unit_name',
            field=models.CharField(default='', max_length=200),
        ),
    ]