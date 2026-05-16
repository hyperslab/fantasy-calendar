from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Calendar, DisplayConfig, DisplayUnitConfig, DateBookmark


class CalendarUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CalendarUpdateForm, self).__init__(*args, **kwargs)
        if self.instance.default_display_config:
            self.fields['default_time_unit_page'] = forms.ModelChoiceField(
                DisplayUnitConfig.objects.filter(display_config_id=self.instance.default_display_config.pk),
                initial=self.instance.default_display_config.default_display_unit_config.pk
                    if self.instance.default_display_config.default_display_unit_config else None,
                help_text=DisplayConfig._meta.get_field('default_display_unit_config').help_text)
            self.fields['default_date_bookmark'] = forms.ModelChoiceField(
                DateBookmark.objects.filter(calendar_id=self.instance.pk), required=False,
                initial=self.instance.default_display_config.default_date_bookmark.pk
                    if self.instance.default_display_config.default_date_bookmark else None,
                help_text=DisplayConfig._meta.get_field('default_date_bookmark').help_text)

    class Meta:
        model = Calendar
        fields = ['calendar_name', 'world_link_iteration']

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.default_display_config:
            time_unit_key = cleaned_data['default_time_unit_page'].time_unit.pk
            sub_unit_key = cleaned_data['default_time_unit_page'].sub_unit.pk \
                if cleaned_data['default_time_unit_page'].sub_unit else None
            if cleaned_data['default_date_bookmark']:
                if cleaned_data['default_date_bookmark'].bookmark_unit.pk != time_unit_key:
                    self.add_error('default_date_bookmark',
                                   ValidationError(_("Error: default bookmark's time unit does not match display "
                                                     "unit!"), code='invalid'))
                elif ((sub_unit_key and not cleaned_data['default_date_bookmark'].bookmark_sub_unit) or
                      (not sub_unit_key and cleaned_data['default_date_bookmark'].bookmark_sub_unit) or
                      (sub_unit_key and cleaned_data['default_date_bookmark'].bookmark_sub_unit and
                       cleaned_data['default_date_bookmark'].bookmark_sub_unit.pk != sub_unit_key)):
                    self.add_error('default_date_bookmark',
                                   ValidationError(_("Error: default bookmark's sub unit does not match display sub "
                                                     "unit!"), code='invalid'))
        return cleaned_data


class DisplayConfigCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DisplayConfigCreateForm, self).__init__(*args, **kwargs)
        self.fields['default_time_unit_page'] = forms.ChoiceField(
            help_text=DisplayConfig._meta.get_field('default_display_unit_config').help_text)

    class Meta:
        model = DisplayConfig
        fields = ['display_config_name', 'default_date_bookmark']

    def clean(self):
        cleaned_data = super().clean()
        time_unit_key = int(cleaned_data['default_time_unit_page'].split(',')[0])
        sub_unit_key = int(cleaned_data['default_time_unit_page'].split(',')[1]) \
            if cleaned_data['default_time_unit_page'].split(',')[1] else None
        if cleaned_data['default_date_bookmark']:
            if cleaned_data['default_date_bookmark'].bookmark_unit.pk != time_unit_key:
                self.add_error('default_date_bookmark',
                               ValidationError(_("Error: default bookmark's time unit does not match display unit!"),
                                               code='invalid'))
            elif ((sub_unit_key and not cleaned_data['default_date_bookmark'].bookmark_sub_unit) or
                  (not sub_unit_key and cleaned_data['default_date_bookmark'].bookmark_sub_unit) or
                  (sub_unit_key and cleaned_data['default_date_bookmark'].bookmark_sub_unit and
                  cleaned_data['default_date_bookmark'].bookmark_sub_unit.pk != sub_unit_key)):
                self.add_error('default_date_bookmark',
                               ValidationError(_("Error: default bookmark's sub unit does not match display sub unit!"),
                                               code='invalid'))
        return cleaned_data


class DisplayConfigUpdateForm(forms.ModelForm):
    class Meta:
        model = DisplayConfig
        fields = ['display_config_name', 'default_display_unit_config', 'default_date_bookmark']

    def clean(self):
        cleaned_data = super().clean()
        time_unit_key = cleaned_data['default_display_unit_config'].time_unit.pk
        sub_unit_key = cleaned_data['default_display_unit_config'].sub_unit.pk \
            if cleaned_data['default_display_unit_config'].sub_unit else None
        if cleaned_data['default_date_bookmark']:
            if cleaned_data['default_date_bookmark'].bookmark_unit.pk != time_unit_key:
                self.add_error('default_date_bookmark',
                               ValidationError(_("Error: default bookmark's time unit does not match display unit!"),
                                               code='invalid'))
            elif ((sub_unit_key and not cleaned_data['default_date_bookmark'].bookmark_sub_unit) or
                  (not sub_unit_key and cleaned_data['default_date_bookmark'].bookmark_sub_unit) or
                  (sub_unit_key and cleaned_data['default_date_bookmark'].bookmark_sub_unit and
                   cleaned_data['default_date_bookmark'].bookmark_sub_unit.pk != sub_unit_key)):
                self.add_error('default_date_bookmark',
                               ValidationError(_("Error: default bookmark's sub unit does not match display sub unit!"),
                                               code='invalid'))
        return cleaned_data


class DisplayUnitConfigCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DisplayUnitConfigCreateForm, self).__init__(*args, **kwargs)
        self.fields['time_unit_page'] = forms.ChoiceField()

    class Meta:
        model = DisplayUnitConfig
        fields = []


class DisplayUnitConfigUpdateForm(forms.ModelForm):
    class Meta:
        model = DisplayUnitConfig
        fields = ['search_type', 'searchable_date_formats', 'header_display_name_type', 'header_other_date_format',
                  'sub_unit_display_name_type', 'sub_unit_other_date_format', 'row_grouping_time_unit',
                  'row_grouping_label_type', 'block_grouping_time_unit', 'show_events', 'max_events_per_instance',
                  'show_linked_instance_display_names', 'linked_instance_display_name_type',
                  'show_linked_instance_events']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['searchable_date_formats']:
            checked_formats = []
            for date_format in cleaned_data['searchable_date_formats']:
                if not date_format.is_reversible():
                    self.add_error('searchable_date_formats',
                                   ValidationError(_("Error: date format " + str(date_format) +
                                                     " is not fully reversible and cannot be searched on!"),
                                                   code='invalid'))
                elif checked_formats and not date_format.is_differentiable(checked_formats):
                    self.add_error('searchable_date_formats',
                                   ValidationError(_("Error: date format " + str(date_format) +
                                                     " is not differentiable from at least one other date format "
                                                     "marked as searchable and cannot be searched on!"),
                                                   code='invalid'))
                checked_formats.append(date_format)
        if cleaned_data['row_grouping_time_unit']:
            if len(cleaned_data['row_grouping_time_unit'].get_expanded_length_cycle()) > 1:
                self.add_error('row_grouping_time_unit',
                               ValidationError(_("Error: row grouping time unit has a variable length cycle!")))
            elif len(cleaned_data['row_grouping_time_unit'].get_expanded_length_cycle()) < 1:
                self.add_error('row_grouping_time_unit',
                               ValidationError(_("Error: row grouping time unit has no length cycle!")))
        return cleaned_data

class DateBookmarkCreateForm(forms.ModelForm):
    class Meta:
        model = DateBookmark
        fields = ['date_bookmark_name', 'bookmark_unit', 'bookmark_iteration', 'bookmark_sub_unit']

    def clean(self):
        cleaned_data = super().clean()
        if (cleaned_data['bookmark_sub_unit'] and cleaned_data['bookmark_unit'].pk not in
                [sub_unit.pk for sub_unit in cleaned_data['bookmark_sub_unit'].get_all_higher_containing_units()]):
            self.add_error('bookmark_sub_unit',
                           ValidationError(_("Error: bookmark sub unit is not a valid sub unit of time unit!"),
                                           code='invalid'))
        return cleaned_data
