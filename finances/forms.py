#-*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.forms import ModelForm
from django.forms.widgets import PasswordInput, DateInput, TextInput
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.utils.timezone import now
import re

from users.models import User
from finances.models import Cheque, Cash, Lydia, BankAccount, SharedEvent
from borgia.validators import *


class TransfertCreateForm(forms.Form):
    recipient = forms.CharField(label='Receveur', max_length=255,
                                widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                                validators=[autocomplete_username_validator])
    amount = forms.DecimalField(label='Montant (€)', decimal_places=2, max_digits=9, min_value=0)

    def __init__(self, **kwargs):
        self.request = kwargs.pop('request')
        super(TransfertCreateForm, self).__init__(**kwargs)

    def clean(self):
        cleaned_data = super(TransfertCreateForm, self).clean()
        try:
            recipient = cleaned_data['recipient']
            amount = cleaned_data['amount']

            if User.objects.get(username=recipient) == self.request.user:
                raise forms.ValidationError('Transfert vers soi-même impossible')

            if amount > self.request.user.balance:
                raise forms.ValidationError('Le montant doit être inférieur ou égal à ton solde.')
        except KeyError:
            pass
        return cleaned_data


class SupplyUnitedForm(forms.Form):

    # Général
    # Type
    type = forms.ChoiceField(label='Type', choices=(('cash', 'Espèces'), ('cheque', 'Chèque'), ('lydia', 'Lydia')))
    # Informations générales
    amount = forms.DecimalField(label='Montant (€)', decimal_places=2, max_digits=9, min_value=0)
    sender = forms.CharField(label='Payeur', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                             validators=[autocomplete_username_validator])
    unique_number = forms.CharField(label='Numéro unique', required=False)  # Inutile pour Cash
    signature_date = forms.DateField(label='Date de signature', required=False,
                                     widget=forms.DateInput(attrs={'class': 'datepicker'}))  # Inutile pour Cash
    bank_account = forms.CharField(label='Compte bancaire', widget=forms.Select,
                                   required=False)  # Inutile pour Cash et Lydia

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire',
                                        widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                                        validators=[autocomplete_username_validator])
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean_unique_number(self):
        data = self.cleaned_data['unique_number']

        # Cas chèque -> obligatoire et bon format
        if self.cleaned_data['type'] == 'cheque':
            if re.match('^[0-9]{7}$', data) is None:
                raise forms.ValidationError('Numéro de chèque invalide')

        # Cas Lydia -> obligatoire
        if self.cleaned_data['type'] == 'lydia':
            if data == '':
                raise forms.ValidationError('Obligatoire')

        return data

    def clean_signature_date(self):
        data = self.cleaned_data['signature_date']

        # Cas chèque et lydia -> obligatoire
        if self.cleaned_data['type'] == 'cheque' or self.cleaned_data['type'] == 'lydia':
            if data is None:
                raise forms.ValidationError('Obligatoire')

        return data

    def clean_bank_account(self):
        data = self.cleaned_data['bank_account']

        # Cas chèque -> obligatoire
        if self.cleaned_data['type'] == 'cheque':
            if data == '':
                raise forms.ValidationError('Obligatoire')

        return data

    def clean(self):

        cleaned_data = super(SupplyUnitedForm, self).clean()

        try:
            operator_username = cleaned_data['operator_username']
            operator_password = cleaned_data['operator_password']

            # Essaye d'authentification seulement si les deux champs sont valides
            if operator_password and operator_password:
                # Cas d'échec d'authentification
                if authenticate(username=operator_username, password=operator_password) is None:
                    raise forms.ValidationError('Echec d\'authentification')
                elif authenticate(username=operator_username, password=operator_password).has_perm('users.supply_account') is False:
                    raise forms.ValidationError('Erreur de permission')
        except KeyError:
            pass

        return cleaned_data


class SupplyLydiaSelfForm(forms.Form):

    def __init__(self, **kwargs):
        min_value = kwargs.pop('min_value')
        max_value = kwargs.pop('max_value')
        super(SupplyLydiaSelfForm, self).__init__(**kwargs)
        self.fields['amount'] = forms.DecimalField(label='Montant (€)', decimal_places=2, max_digits=9,
                                                   min_value=min_value,
                                                   max_value=max_value)
        self.fields['tel_number'] = forms.CharField(label='Numéro de téléphone',
                                                    validators=[RegexValidator('^0[0-9]{9}$',
                                                                              'Le numéro de téléphone doit être du type 0123456789')])


class RetrieveMoneyForm(forms.Form):

    date_begin = forms.DateField(label='Date de début', widget=forms.DateInput(attrs={'class': 'datepicker'}))
    date_end = forms.DateField(label='Date de fin', widget=forms.DateInput(attrs={'class': 'datepicker'}))
    all = forms.BooleanField(label='Selectionner tous les opérateurs', required=False)

    def __init__(self, *args, **kwargs):
        user_list = kwargs.pop('user_list')
        super(RetrieveMoneyForm, self).__init__(*args, **kwargs)

        for (i, u) in enumerate(user_list):
            self.fields['field_user_%s' % i] = forms.BooleanField(label=str(u.username + ' ' + u.__str__()), required=False)

    def user_list_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_user_'):
                yield (self.fields[name].label, value)


class ExceptionnalMovementForm(forms.Form):
    type_movement = forms.ChoiceField(choices=(('debit', 'Débit'), ('credit', 'Crédit')), label='Type')
    amount = forms.DecimalField(label='Montant (€)', decimal_places=2, max_digits=9, min_value=0)
    affected = forms.CharField(label='Concerné', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                               validators=[autocomplete_username_validator])
    operator_username = forms.CharField(label='Gestionnaire',
                                        widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                                        validators=[autocomplete_username_validator])
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean(self):

        cleaned_data = super(ExceptionnalMovementForm, self).clean()
        try:
            operator_username = cleaned_data['operator_username']
            operator_password = cleaned_data['operator_password']

            # Cas d'échec d'authentification
            if authenticate(username=operator_username, password=operator_password) is None:
                raise forms.ValidationError('Echec d\'authentification')
            elif authenticate(username=operator_username, password=operator_password).has_perm(
                    'users.exceptionnal_movement') is False:
                raise forms.ValidationError('Erreur de permission')

        except KeyError:
            pass

        return super(ExceptionnalMovementForm, self).clean()


class SharedEventCreateForm(forms.Form):
    description = forms.CharField(label='Description')
    date = forms.DateField(label='Date de l\'événement', widget=forms.DateInput(attrs={'class': 'datepicker'}))
    price = forms.DecimalField(label='Prix total (vide si pas encore connu)', decimal_places=2, max_digits=9,
                               required=False, min_value=0)
    bills = forms.CharField(label='Factures liées (vide si pas encore connu)', required=False)


class SharedEventManageListForm(forms.Form):
    date_begin = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))
    date_end = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))
    all = forms.BooleanField(required=False, label='Depuis toujours')
    done = forms.ChoiceField(choices=((True, 'Terminé'), (False, 'En cours'), ('both', 'Les deux')))
    order_by = forms.ChoiceField(label='Trier par', choices=(('-date', 'Date'), ('manager', 'Opérateur')))


class SharedEventManageUserListForm(forms.Form):
    order_by = forms.ChoiceField(label='Trier par', choices=(('last_name', 'Nom'), ('surname', 'Bucque')))
    state = forms.ChoiceField(label='Lister les', choices=(('registered', 'Inscrits'), ('participants', 'Participants')))


class SharedEventManageUploadJSONForm(forms.Form):
    file = forms.FileField(label='Fichier de données')
    token = forms.ChoiceField(label='Le fichier contient des :', choices=((True, 'Numéros de jetons'),
                                                                          (False, 'Noms d\'utilisateurs')))
    state = forms.ChoiceField(choices=(('registered', 'Inscrit'), ('participants', 'Participant')))


class SharedEventManageUpdateForm(forms.Form):
    price = forms.DecimalField(label='Prix total (€)', decimal_places=2, max_digits=9, min_value=0, required=False)
    bills = forms.CharField(label='Factures liées', required=False)


class SharedEventManageAddForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                               validators=[autocomplete_username_validator])
    state = forms.ChoiceField(choices=(('registered', 'Inscrit'), ('participant', 'Participant')))
    ponderation = forms.IntegerField(label='Pondération', min_value=0, required=False)

    def clean_ponderation(self):
        data = self.cleaned_data['ponderation']

        if self.cleaned_data['state'] == 'participant':
            if data == '':
                raise ValidationError('Obligatoire')

        return data


class SharedEventManageDownloadXlsxForm(forms.Form):
    state = forms.ChoiceField(label='Selection',
                              choices=(('year', 'Listes de promotions'), ('registered', 'Inscrits'),
                                       ('participants', 'Participants')))

    def __init__(self, *args, **kwargs):
        list_year = kwargs.pop('list_year')
        super(SharedEventManageDownloadXlsxForm, self).__init__(*args, **kwargs)

        for (i, y) in enumerate(list_year):
            self.fields['field_year_%s' % i] = forms.BooleanField(label=y, required=False)

    def year_pg_list_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_year_pg_'):
                yield (self.fields[name].label, value)


class SetPriceProductBaseForm(forms.Form):
    is_manual = forms.BooleanField(label='Gestion manuelle du prix', required=False)
    manual_price = forms.DecimalField(label='Prix manuel', decimal_places=2, max_digits=9, min_value=0, required=False)


class BankAccountCreateForm(forms.Form):
    owner = forms.CharField(label='Possesseur', max_length=255,
                            widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                            validators=[autocomplete_username_validator])
    bank = forms.CharField(label='Banque')
    account = forms.CharField(label='Numéro de compte')
