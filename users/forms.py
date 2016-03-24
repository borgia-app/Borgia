#-*- coding: utf-8 -*-
from django import forms
from users.models import User
from django.forms.widgets import PasswordInput
from django.core.exceptions import ObjectDoesNotExist


# Formulaire de creation d'un user
class UserCreationCustomForm(forms.Form):

    username = forms.CharField(label='Username', max_length=255)
    first_name = forms.CharField(label='Prenom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    surname = forms.CharField(label='Buque', max_length=255)
    family = forms.CharField(label='Fam\'ss', max_length=255)
    campus = forms.ChoiceField(label='Tabagn\'s', choices=User.CAMPUS_CHOICES)
    year = forms.ChoiceField(label='Prom\'ss', choices=User.YEAR_CHOICES)
    password = forms.CharField(label='Mot de passe', widget=PasswordInput)
    password_bis = forms.CharField(label='Mot de passe (confirmation)', widget=PasswordInput)

    def clean(self):

        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('Un autre user existe avec cet username')

        if self.cleaned_data['password'] != self.cleaned_data['password_bis']:
            raise forms.ValidationError('Les deux mots de passe ne correspondent pas')


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


class LinkTokenUserForm(forms.Form):
    username = forms.CharField(label='User à lié')
    token_id = forms.CharField(label='Numéro unique du jeton')

    def clean(self):

        cleaned_data = super(LinkTokenUserForm, self).clean()

        # Validation de l'username
        username = cleaned_data['username']
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Cette personne n\'existe pas')

        return super(LinkTokenUserForm, self).clean()


class UserListCompleteForm(forms.Form):

    order_by = forms.ChoiceField(label='Trier par',
                                 choices=(('surname', 'Bucque'), ('balance', 'Solde'),
                                          ('last_name', 'Nom de famille'), ('first_name', 'Prénom')))
    all = forms.BooleanField(label='Selectionner tout les users', required=False)

    def __init__(self, **kwargs):
        list_year = kwargs.pop('list_year')
        super(UserListCompleteForm, self).__init__(**kwargs)

        for (i, y) in enumerate(list_year):
            self.fields['field_year_%s' % i] = forms.BooleanField(label=y, required=False)

    def year_pg_list_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_year_pg_'):
                yield (self.fields[name].label, value)
