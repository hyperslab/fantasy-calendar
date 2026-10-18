from django import forms

class DateFormatPicker(forms.Widget):
    template_name = 'fantasycalendar/date_format_picker.html'

    def __init__(self, attrs=None, units_and_parents=None):
        super(DateFormatPicker, self).__init__(attrs)
        self.units_and_parents = units_and_parents

    def get_context(self, name, value, attrs):
        context = super(DateFormatPicker, self).get_context(name, value, attrs)
        context['units_and_parents'] = self.units_and_parents
        return context
