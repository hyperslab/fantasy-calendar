# Generated by Django 4.2 on 2023-05-02 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calendar_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='World',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('world_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TimeUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_unit_name', models.CharField(max_length=200)),
                ('number_of_base', models.DecimalField(decimal_places=3, default=0, max_digits=8, verbose_name='number of base units in this unit')),
                ('base_unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fantasycalendar.timeunit')),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasycalendar.calendar')),
            ],
        ),
        migrations.AddField(
            model_name='calendar',
            name='world',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasycalendar.world'),
        ),
    ]
