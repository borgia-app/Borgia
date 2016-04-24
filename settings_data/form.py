from django import forms
from django.forms.widgets import TextInput, Textarea
from django.core.exceptions import ValidationError


class UpdateSettingForm(forms.Form):
    value = forms.CharField(label='Valeur')

    def __init__(self, *args, **kwargs):
        self.setting = kwargs.pop('setting')
        super(UpdateSettingForm, self).__init__(*args, **kwargs)

    def clean_value(self):
        data = self.cleaned_data['value']

        types = {
            's': str,
            'i': int,
            'f': float,
            'b': (lambda v: v.lower().startswith('t') or v.startswith('1'))
        }

        try:
            types[self.setting.value_type](data)
        except ValueError:
            raise ValidationError('Erreur de type')

        return data
