from django import forms
from accounts.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class ChangeInformationsForm(forms.Form):
    new_surname = forms.CharField(label='Buque', max_length=255)
    new_family = forms.CharField(label='Fam\'ss', max_length=255)
    new_campus = forms.CharField(label='Tabagn\'ss', max_length=4)
    new_year = forms.IntegerField(label='Prom\'ss')


class UserCreationCustomForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'surname', 'family', 'campus', 'year')

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            self.Meta.model.objects.get(username=username)
        except self.Meta.model.DoesNotExist:
            return username

        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    first_name = forms.CharField(label='Prénom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    surname = forms.CharField(label='Buque', max_length=255)
    family = forms.CharField(label='Fam\'ss', max_length=255)
    campus = forms.CharField(label='Tabagn\'s', max_length=2)
    year = forms.IntegerField(label='Prom\'ss')


class UserUpdateCustomForm(UserChangeForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'surname', 'family', 'campus', 'year')

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            self.Meta.model.objects.get(username=username)
        except self.Meta.model.DoesNotExist:
            return username

        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    first_name = forms.CharField(label='Prénom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    surname = forms.CharField(label='Buque', max_length=255)
    family = forms.CharField(label='Fam\'ss', max_length=255)
    campus = forms.CharField(label='Tabagn\'s', max_length=2)
    year = forms.IntegerField(label='Prom\'ss')