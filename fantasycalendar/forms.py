from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import DisplayConfig, DisplayUnitConfig


class DisplayConfigCreateForm(forms.ModelForm):
    class Meta:
        model = DisplayConfig
        fields = ['display_config_name', 'display_unit', 'nest_level', 'default_date_bookmark']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['default_date_bookmark']:
            if cleaned_data['default_date_bookmark'].bookmark_unit != cleaned_data['display_unit']:
                self.add_error('default_date_bookmark',
                               ValidationError(_("Error: default bookmark's time unit does not match display unit!"),
                                               code='invalid'))
        return cleaned_data


class DisplayConfigUpdateForm(forms.ModelForm):
    class Meta:
        model = DisplayConfig
        fields = ['display_config_name', 'display_unit', 'nest_level', 'default_date_bookmark']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['default_date_bookmark']:
            if cleaned_data['default_date_bookmark'].bookmark_unit != cleaned_data['display_unit']:
                self.add_error('default_date_bookmark',
                               ValidationError(_("Error: default bookmark's time unit does not match display unit!"),
                                               code='invalid'))
        return cleaned_data


class DisplayUnitConfigUpdateForm(forms.ModelForm):
    class Meta:
        model = DisplayUnitConfig
        fields = ['search_type', 'searchable_date_formats', 'header_display_name_type', 'header_other_date_format',
                  'base_unit_display_name_type', 'base_unit_other_date_format', 'row_grouping_time_unit',
                  'row_grouping_label_type']

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
                if checked_formats:
                    if not date_format.is_differentiable(checked_formats):
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
            if len(cleaned_data['row_grouping_time_unit'].get_expanded_length_cycle()) < 1:
                self.add_error('row_grouping_time_unit',
                               ValidationError(_("Error: row grouping time unit has no length cycle!")))
        return cleaned_data
