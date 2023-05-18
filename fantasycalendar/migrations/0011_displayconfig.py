# Generated by Django 4.2.1 on 2023-05-18 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantasycalendar', '0010_timeunit_default_date_format'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisplayConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_config_name', models.CharField(max_length=200)),
                ('nest_level', models.IntegerField(default=0)),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasycalendar.calendar')),
                ('display_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasycalendar.timeunit')),
            ],
        ),
    ]
