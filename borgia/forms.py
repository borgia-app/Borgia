from django import forms

class UserSearchForm(forms.Form):
    search = forms.CharField(
        label='Recherche',
        max_length=255
    )
