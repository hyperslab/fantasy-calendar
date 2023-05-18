from django.contrib import admin
from django.urls import resolve
from django import forms

from .models import World, Calendar, TimeUnit, Event, DateFormat, DisplayConfig


class TimeUnitInLineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TimeUnitInLineForm, self).__init__(*args, **kwargs)
        self.fields['base_unit'].queryset = self.fields['base_unit'].queryset.exclude(id=self.instance.id)
        if self.instance.is_bottom_level():
            # better result would be to hide the field completely but this doesn't seem easily possible
            # closest ask I've found: https://stackoverflow.com/questions/12178074/django-how-to-remove-one-field-from-specific-member-of-the-admin-inline
            self.fields['base_unit'].queryset = TimeUnit.objects.none()


class TimeUnitInLine(admin.TabularInline):
    model = TimeUnit
    extra = 1
    form = TimeUnitInLineForm
    fields = ['time_unit_name', 'base_unit', 'length_cycle', 'is_bottom_level', 'base_unit_instance_names']
    readonly_fields = ['is_bottom_level']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super(TimeUnitInLine, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'base_unit':
            resolved = resolve(request.path_info)
            if 'object_id' in resolved.kwargs:
                field.queryset = field.queryset.filter(calendar_id__exact=resolved.kwargs['object_id'])
        return field


class CalendarAdmin(admin.ModelAdmin):
    fields = ('calendar_name',)
    inlines = [TimeUnitInLine]


admin.site.register(Calendar, CalendarAdmin)


class CalendarInLine(admin.StackedInline):
    model = Calendar
    extra = 1
    show_change_link = True


class WorldAdmin(admin.ModelAdmin):
    fields = ('world_name',)
    inlines = [CalendarInLine]


admin.site.register(World, WorldAdmin)


class EventAdmin(admin.ModelAdmin):
    fields = ('calendar', 'event_name', 'event_description', 'bottom_level_iteration')


admin.site.register(Event, EventAdmin)


class DateFormatAdmin(admin.ModelAdmin):
    fields = ('calendar', 'time_unit', 'date_format_name', 'format_string')


admin.site.register(DateFormat, DateFormatAdmin)


class DisplayConfigAdmin(admin.ModelAdmin):
    fields = ('calendar', 'display_config_name', 'display_unit', 'nest_level')


admin.site.register(DisplayConfig, DisplayConfigAdmin)
