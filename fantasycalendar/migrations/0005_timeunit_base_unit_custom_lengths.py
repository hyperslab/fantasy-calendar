# Generated by Django 4.2.1 on 2023-05-10 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasycalendar', '0004_alter_timeunit_base_unit_instance_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeunit',
            name='base_unit_custom_lengths',
            field=models.CharField(blank=True, default='', max_length=800),
        ),
    ]