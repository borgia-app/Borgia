#-*- coding: utf-8 -*-
from django import forms
from users.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission, Group


# Formulaire de creation d'un user
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

    username = forms.CharField(label='Username', max_length=255)
    first_name = forms.CharField(label='Prenom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    surname = forms.CharField(label='Buque', max_length=255)
    family = forms.CharField(label='Fam\'ss', max_length=255)
    campus = forms.ChoiceField(label='Tabagn\'s', choices=User.CAMPUS_CHOICES)
    year = forms.ChoiceField(label='Prom\'ss', choices=User.YEAR_CHOICES)


# Formulaire de modification d'un groupe
class ManageGroupForm(forms.Form):

    def __init__(self, *args, **kwargs):

        possible_members = kwargs.pop('possible_members')
        possible_permissions = kwargs.pop('possible_permissions')
        super(ManageGroupForm, self).__init__(*args, **kwargs)

        self.fields['members'] = forms.ModelMultipleChoiceField(label='Membres', queryset=possible_members,
                                                                required=False)
        # Utilisation d'un custom field pour pouvoir changer l'affichage des permissions
        self.fields['permissions'] = ModelMultipleChoiceCustomField(label='Permissions', queryset=possible_permissions,
                                                                    required=False)


class ModelMultipleChoiceCustomField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name
