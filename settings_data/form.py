from django import forms
from django.forms.widgets import TextInput, Textarea


class UpdateSettingForm(forms.Form):
    name = forms.CharField(label='Nom', widget=TextInput(attrs={'disabled': 'disabled'}), required=False)
    description = forms.CharField(label='Description', widget=Textarea(attrs={'disabled': 'disabled'}), required=False)
    value = forms.CharField(label='Valeur')
    value_type = forms.CharField(label='Type', widget=TextInput(attrs={'disabled': 'disabled'}), required=False)
