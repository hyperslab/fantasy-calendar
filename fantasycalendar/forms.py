from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import DisplayConfig


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

