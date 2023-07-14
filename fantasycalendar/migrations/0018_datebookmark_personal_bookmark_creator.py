# Generated by Django 4.2.1 on 2023-07-14 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fantasycalendar', '0017_alter_timeunit_default_date_format_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='datebookmark',
            name='personal_bookmark_creator',
            field=models.ForeignKey(blank=True, help_text='<span class="tooltip">?<span class="tooltip-text">The creator of this bookmark if this is a personal bookmark; not populated if this is a shared bookmark</span></span>', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
