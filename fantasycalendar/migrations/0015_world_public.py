# Generated by Django 4.2.1 on 2023-06-02 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasycalendar', '0014_world_creator_alter_calendar_default_display_config_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='world',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]