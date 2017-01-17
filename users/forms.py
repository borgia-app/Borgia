#-*- coding: utf-8 -*-
from django import forms
from users.models import User
from django.forms.widgets import PasswordInput
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.admin.widgets import FilteredSelectMultiple
from borgia.validators import *


# Formulaire de creation d'un user
class UserCreationCustomForm(forms.Form):

    username = forms.CharField(label='Username', max_length=255)
    first_name = forms.CharField(label='Prenom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    email = forms.EmailField(label='Email')
    surname = forms.CharField(label='Buque', max_length=255, required=False)
    family = forms.CharField(label='Fam\'ss', max_length=255, required=False)
    campus = forms.ChoiceField(label='Tabagn\'s', choices=User.CAMPUS_CHOICES, required=False)
    year = forms.ChoiceField(label='Prom\'ss', choices=User.YEAR_CHOICES, required=False)
    honnor_member = forms.BooleanField(label='Membre d\'honneur', required=False)
    password = forms.CharField(label='Mot de passe', widget=PasswordInput)
    password_bis = forms.CharField(label='Mot de passe (confirmation)', widget=PasswordInput)

    def clean(self):
        cleaned_data = super(UserCreationCustomForm, self).clean()
        try:

            if cleaned_data['password'] != cleaned_data['password_bis']:
                raise forms.ValidationError('Les deux mots de passe ne correspondent pas')

        except KeyError:
            pass
        return super(UserCreationCustomForm, self).clean()

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            raise ValidationError('Un autre user existe avec cet username')
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise ValidationError('Cet email est déjà utilisé')
        return data


class UserUpdateForm(forms.Form):
    email = forms.EmailField(label='Email')
    phone = forms.CharField(label='Téléphone', required=False)
    avatar = forms.ImageField(label='Avatar', required=False)

    def __init__(self, **kwargs):
        self.user_modified = kwargs.pop('user_modified')
        super(UserUpdateForm, self).__init__(**kwargs)

    def clean_email(self):
        data = self.cleaned_data['email']
        if data == '':
            raise ValidationError('Ce champ ne peut pas être vide')
        if User.objects.filter(email=data).exclude(pk=self.user_modified.pk).exists():
            raise ValidationError('Un autre user existe avec cet email')
        return data


class UserUpdateAdminForm(forms.Form):
    first_name = forms.CharField(label='Prenom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    email = forms.EmailField(label='Email')
    surname = forms.CharField(label='Buque', max_length=255, required=False)
    family = forms.CharField(label='Fam\'ss', max_length=255, required=False)
    campus = forms.ChoiceField(label='Tabagn\'s', choices=User.CAMPUS_CHOICES, required=False)
    year = forms.ChoiceField(label='Prom\'ss', choices=User.YEAR_CHOICES, required=False)

    def __init__(self, **kwargs):
        self.user_modified = kwargs.pop('user_modified')
        super(UserUpdateAdminForm, self).__init__(**kwargs)

    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if data == '':
            raise ValidationError('Ce champ ne peut pas être vide')
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        if data == '':
            raise ValidationError('Ce champ ne peut pas être vide')
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if data == '':
            raise ValidationError('Ce champ ne peut pas être vide')
        if User.objects.filter(email=data).exclude(pk=self.user_modified.pk).exists():
            raise ValidationError('Un autre user existe avec cet email')
        return data


# Formulaire de modification d'un groupe
class ManageGroupForm(forms.Form):

    class Media:
        js = ('/local/jsi18n',)

    def __init__(self, *args, **kwargs):

        possible_members = kwargs.pop('possible_members')
        possible_permissions = kwargs.pop('possible_permissions')
        super(ManageGroupForm, self).__init__(*args, **kwargs)
        self.fields['members'] = forms.ModelMultipleChoiceField(queryset=possible_members,
                                                                widget=FilteredSelectMultiple('Membres', False),
                                                                required=False)
        self.fields['permissions'] = forms.ModelMultipleChoiceField(queryset=possible_permissions,
                                                                    widget=FilteredSelectMultiple('Permissions', False),
                                                                    required=False)


class LinkTokenUserForm(forms.Form):
    username = forms.CharField(label='User à lier', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}))
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

    all = forms.BooleanField(label='Selectionner toutes les promotions', required=False)
    unactive = forms.BooleanField(label='Utilisateurs désactivés', required=False)

    def __init__(self, **kwargs):
        list_year = kwargs.pop('list_year')
        super(UserListCompleteForm, self).__init__(**kwargs)

        for (i, y) in enumerate(list_year):
            self.fields['field_year_%s' % i] = forms.BooleanField(label=y, required=False)

    def year_pg_list_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_year_pg_'):
                yield (self.fields[name].label, value)
