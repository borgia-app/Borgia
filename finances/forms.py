#-*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.forms import ModelForm
from django.forms.widgets import PasswordInput, DateInput, TextInput
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
import re

from users.models import User
from finances.models import Cheque, Cash, Lydia, BankAccount, SharedEvent


class TransfertCreateForm(forms.Form):
    recipient = forms.CharField(label='Receveur', max_length=255,
                                widget=forms.TextInput(attrs={'class': 'autocomplete_username'}))
    amount = forms.IntegerField(label='Montant')

    def __init__(self, **kwargs):
        self.request = kwargs.pop('request')
        super(TransfertCreateForm, self).__init__(**kwargs)

    def clean(self):
        cleaned_data = super(TransfertCreateForm, self).clean()
        recipient = cleaned_data['recipient']
        try:
            User.objects.get(username=recipient)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Cette personne n\'existe pas')

        if User.objects.get(username=recipient) == self.request.user:
            raise forms.ValidationError('Transfert vers soi-même impossible')


class SupplyUnitedForm(forms.Form):

    # Général
    # Type
    type = forms.ChoiceField(label='Type', choices=(('cash', 'Espèces'), ('cheque', 'Chèque'), ('lydia', 'Lydia')))
    # Informations générales
    amount = forms.FloatField(label='Montant (€)')
    sender = forms.CharField(label='Payeur', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}))
    unique_number = forms.CharField(label='Numéro unique', required=False)  # Inutile pour Cash
    signature_date = forms.DateField(label='Date de signature', required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))  # Inutile pour Cash
    bank_account = forms.ModelChoiceField(label='Compte bancaire', queryset=BankAccount.objects.all(),
                                          required=False)  # Inutile pour Cash et Lydia

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}))
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean(self):

        cleaned_data = super(SupplyUnitedForm, self).clean()
        operator_username = cleaned_data['operator_username']
        operator_password = cleaned_data['operator_password']

        # Essaye d'authentification seulement si les deux champs sont valides
        if operator_password and operator_password:
            # Cas d'échec d'authentification
            if authenticate(username=operator_username, password=operator_password) is None:
                raise forms.ValidationError('Echec d\'authentification')
            elif authenticate(username=operator_username, password=operator_password).has_perm('users.supply_account') is False:
                raise forms.ValidationError('Erreur de permission')
        return super(SupplyUnitedForm, self).clean()


class SupplyLydiaSelfForm(forms.Form):

    def __init__(self, **kwargs):
        min_value = kwargs.pop('min_value')
        max_value = kwargs.pop('max_value')
        super(SupplyLydiaSelfForm, self).__init__(**kwargs)
        self.fields['amount'] = forms.DecimalField(label='Montant (€)', decimal_places=2, max_digits=9,
                                                   min_value=min_value,
                                                   max_value=max_value)
        self.fields['tel_number'] = forms.CharField(label='Numéro de téléphone')

    def clean(self):
        cleaned_data = super(SupplyLydiaSelfForm, self).clean()
        try:
            tel_number = cleaned_data['tel_number']
            filter_tel_number = re.compile('^0[0-9]{9}$')
            if filter_tel_number.match(tel_number) is None:
                raise forms.ValidationError('Numéro de téléphone incorrect, il doit être du type "0123456789')
        except KeyError:
            pass
        return super(SupplyLydiaSelfForm, self).clean()


class RetrieveMoneyForm(forms.Form):

    date_begin = forms.DateField(label='Date de début', widget=forms.DateInput(attrs={'class': 'datepicker'}))
    date_end = forms.DateField(label='Date de fin', widget=forms.DateInput(attrs={'class': 'datepicker'}))
    order_by = forms.ChoiceField(label='Tri par',
                                 choices=(('operator', 'Opérateur'), ('date', 'Date'), ('amount', 'Montant')))

    def __init__(self, *args, **kwargs):
        user_list = kwargs.pop('user_list')
        super(RetrieveMoneyForm, self).__init__(*args, **kwargs)

        for (i, u) in enumerate(user_list):
            self.fields['field_user_%s' % i] = forms.BooleanField(label=str(u.username + ' ' + u.__str__()), required=False)

    def user_list_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_user_'):
                yield (self.fields[name].label, value)


class SharedEventCreateForm(forms.Form):
    description = forms.CharField(label='Description')
    date = forms.DateField(label='Date de l\'événement', widget=forms.DateInput(attrs={'class': 'datepicker'}))
    price = forms.DecimalField(label='Prix total (vide si pas encore connu)', decimal_places=2, max_digits=9,
                               required=False)
    bills = forms.CharField(label='Factures liées (vide si pas encore connu)', required=False)


class SharedEventRegistrationForm(forms.Form):
    shared_event = forms.ModelChoiceField(label='S\'inscrire à l\'événement :',
                                          queryset=SharedEvent.objects.filter(done=False, date__gte=now()))

    def __init__(self, **kwargs):
        self.request = kwargs.pop('request')
        super(SharedEventRegistrationForm, self).__init__(**kwargs)

    def clean(self):
        se = self.cleaned_data['shared_event']
        if self.request.user in se.registered.all():
            raise forms.ValidationError('Vous êtes déjà inscrit à cet événement')


class SharedEventUpdateForm(forms.Form):
    file = forms.FileField(label='Fichier de données')
    price = forms.DecimalField(label='Prix total', decimal_places=2, max_digits=9)
    bills = forms.CharField(label='Factures liées')
    managing_errors = forms.ChoiceField(label='Que faire en cas d\' erreurs de jeton ?',
                                        choices=(('other_pay_all', 'Répercuter le prix sur les autres participants'),
                                                 ('nothing', 'Ne rien faire (risque de perte sur l\'événement)')))


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
    price = forms.DecimalField(label='Prix total (€)', decimal_places=2, max_digits=9, required=False)
    bills = forms.CharField(label='Factures liées', required=False)


class SharedEventManageAddForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}))
    state = forms.ChoiceField(choices=(('registered', 'Inscrit'), ('participant', 'Participant')))
    ponderation = forms.IntegerField(label='Pondération', min_value=0, required=False)


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
