import re
import datetime

from django import forms
from django.contrib.auth import authenticate
from django.forms.widgets import PasswordInput
from django.core.validators import RegexValidator
from django.db.models import Q
from django.contrib.auth.models import Permission

from users.models import User
from shops.models import Shop
from finances.models import BankAccount
from borgia.validators import *
from users.models import list_year


class BankAccountCreateForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank', 'account']


class BankAccountUpdateForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank', 'account']


class SelfTransfertCreate(forms.Form):
    def __init__(self, **kwargs):
        sender = kwargs.pop('sender')
        super(SelfTransfertCreate, self).__init__(**kwargs)
        self.fields['recipient'] = forms.ModelChoiceField(
            label='Receveur',
            queryset=User.objects.all().exclude(pk__in=[1, sender.pk]),
            widget=forms.Select(
                attrs={'class': 'form-control selectpicker',
                       'data-live-search': 'True'})
            )
        self.fields['amount'] = forms.DecimalField(
            label='Montant (€)',
            decimal_places=2,
            max_digits=9,
            min_value=0, max_value=sender.balance)
        self.fields['justification'] = forms.CharField(
            label='Justification',
            max_length=254
        )


class GenericListSearchDateForm(forms.Form):
    search = forms.CharField(label='Recherche', max_length=255, required=False)
    date_begin = forms.DateField(
        label='Date de début',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False)
    date_end = forms.DateField(
        label='Date de fin',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False)


class SaleListSearchDateForm(forms.Form):
    shop = forms.ModelChoiceField(
        label='Magasin',
        queryset=Shop.objects.all().exclude(pk=1),
        empty_label="Tous",
        required=False)
    search = forms.CharField(label='Recherche', max_length=255, required=False)
    date_begin = forms.DateField(
        label='Date de début',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False)
    date_end = forms.DateField(
        label='Date de fin',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False)


class RechargingListForm(GenericListSearchDateForm):
    def __init__(self, *args, **kwargs):
        super(RechargingListForm, self).__init__(*args, **kwargs)
        try:
            perm = Permission.objects.get(codename='supply_money_user')
            queryset = User.objects.filter(groups__permissions=perm).distinct()
        except ObjectDoesNotExist:
            queryset = User.objects.none()

        self.fields['operators'] = forms.ModelMultipleChoiceField(
            label='Opérateurs',
            queryset=queryset,
            widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                               'data-live-search': 'True'}),
            required=False)


class ExceptionnalMovementForm(forms.Form):
    type_movement = forms.ChoiceField(choices=(('debit', 'Débit'),
                                               ('credit', 'Crédit')),
                                      label='Type')
    amount = forms.DecimalField(label='Montant (€)', decimal_places=2,
                                max_digits=9, min_value=0)
    justification = forms.CharField(label='Justification')
    operator_username = forms.CharField(label='Gestionnaire',
                                        widget=forms.TextInput(
                                            attrs={'class':
                                                   'autocomplete_username'}),
                                        validators=[
                                            autocomplete_username_validator])
    operator_password = forms.CharField(label='Mot de passe',
                                        widget=PasswordInput)

    def clean(self):
        cleaned_data = super(ExceptionnalMovementForm, self).clean()

        try:
            operator_username = cleaned_data['operator_username']
            operator_password = cleaned_data['operator_password']
            if (authenticate(
                username=operator_username,
                    password=operator_password) is None):
                raise forms.ValidationError('Echec d\'authentification')
        except KeyError:
            pass

        return super(ExceptionnalMovementForm, self).clean()


class UserSupplyMoneyForm(forms.Form):
    type = forms.ChoiceField(label='Type', choices=(('cash', 'Espèces'),
                                                    ('cheque', 'Chèque'),
                                                    ('lydia', 'Lydia')))
    amount = forms.DecimalField(label='Montant (€)', decimal_places=2,
                                max_digits=9, min_value=0)
    # Unused for Cash
    unique_number = forms.CharField(label='Numéro unique', required=False)
    # Unused for Cash
    signature_date = forms.DateField(label='Date de signature', required=False,
                                     widget=forms.DateInput(
                                         attrs={'class': 'datepicker'}))
    # Unused for Cash and Lydia
    bank_account = forms.CharField(label='Compte bancaire', required=False)
    operator_username = forms.CharField(label='Gestionnaire',
                                        widget=forms.TextInput(
                                            attrs={'class':
                                                   'autocomplete_username'}),
                                        validators=[
                                            autocomplete_username_validator])
    operator_password = forms.CharField(label='Mot de passe',
                                        widget=PasswordInput)

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        super(UserSupplyMoneyForm, self).__init__(**kwargs)
        self.fields['bank_account'] = forms.ModelChoiceField(
            label='Compte bancaire',
            queryset=BankAccount.objects.filter(owner=self.user),
            required=False
        )

    def clean_unique_number(self):
        data = self.cleaned_data['unique_number']

        if self.cleaned_data['type'] == 'cheque':
            if re.match('^[0-9]{7}$', data) is None:
                raise forms.ValidationError('Numéro de chèque invalide')
        if self.cleaned_data['type'] == 'lydia':
            if data == '':
                raise forms.ValidationError('Obligatoire')

        return data

    def clean_signature_date(self):
        data = self.cleaned_data['signature_date']

        if (self.cleaned_data['type'] == 'cheque'
                or self.cleaned_data['type'] == 'lydia'):
            if data is None:
                raise forms.ValidationError('Obligatoire')

        return data

    def clean_bank_account(self):
        data = self.cleaned_data['bank_account']

        if self.cleaned_data['type'] == 'cheque':
            if data is None:
                raise forms.ValidationError('Obligatoire')

        return data

    def clean(self):

        cleaned_data = super(UserSupplyMoneyForm, self).clean()

        try:
            operator_username = cleaned_data['operator_username']
            operator_password = cleaned_data['operator_password']

            if operator_password and operator_password:
                if (authenticate(
                    username=operator_username,
                        password=operator_password) is None):
                    raise forms.ValidationError('Echec d\'authentification')
        except KeyError:
            pass

        return cleaned_data


class SelfLydiaCreateForm(forms.Form):
    def __init__(self, **kwargs):
        min_value = kwargs.pop('min_value')
        max_value = kwargs.pop('max_value')
        super(SelfLydiaCreateForm, self).__init__(**kwargs)
        self.fields['amount'] = forms.IntegerField(
            label='Montant (€)',
            min_value=min_value,
            max_value=max_value)
        self.fields['tel_number'] = forms.CharField(
            label='Numéro de téléphone',
            validators=[
                RegexValidator(
                    '^0[0-9]{9}$',
                    'Le numéro de téléphone doit être du type 0123456789')
                ])


class SharedEventListForm(forms.Form):
    date_begin = forms.DateField(label="Depuis", required=False, initial= datetime.date.today(),
                                    widget=forms.DateInput(attrs={'class': 'datepicker'})
                                )
    date_end = forms.DateField(label="Jusqu'à", required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))
    done = forms.ChoiceField(label="Etat", choices=(("not_done", 'En cours'), ("done", 'Terminé'), ("both", 'Les deux')),
                                initial=("not_done", 'En cours')
                            )
    order_by = forms.ChoiceField(label="Trier par", choices=(('-date', 'Date'), ('manager', 'Opérateur')))


class SharedEventCreateForm(forms.Form):
    description = forms.CharField(label='Description')
    date = forms.DateField(label='Date de l\'événement', widget=forms.DateInput(attrs={'class': 'datepicker'}))
    price = forms.DecimalField(label='Prix total (vide si pas encore connu)', decimal_places=2, max_digits=9,
                               required=False, min_value=0)
    bills = forms.CharField(label='Factures liées (vide si pas encore connu)', required=False)
    allow_self_registeration = forms.BooleanField(label='Autoriser la self préinscription', initial=True, required=False)
    date_end_registration = forms.DateField(    label='Date de fin de self-préinscription (Si pas autorisé laisser vide)',
                                                required=False,
                                                widget=forms.DateInput(attrs={'class': 'datepicker'})
                                            )


class SharedEventFinishForm(forms.Form):
    remark = forms.CharField(label='Pourquoi finir l\'événement ?')


class SharedEventUpdateForm(forms.Form):
    price = forms.DecimalField(label='Prix total (€)', decimal_places=2, max_digits=9, min_value=0, required=False)
    bills = forms.CharField(label='Factures liées', required=False)
    allow_self_registeration = forms.BooleanField(label='Autoriser la préinscription', required=False)


class SharedEventListUsersForm(forms.Form):
    order_by = forms.ChoiceField(label='Trier par', choices=(('username', 'Username'), ('last_name', 'Nom'), ('surname', 'Bucque')))
    state = forms.ChoiceField(label='Lister les', choices=(('users', 'Tous les concernés'),
                                                ('registrants', 'Uniquement les préinscrit'),
                                                ('participants', 'Uniquement les participant')))


class SharedEventSelfRegistrationForm(forms.Form):
    weight = forms.IntegerField(label='Pondération', min_value=0)


class SharedEventAddWeightForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                               validators=[autocomplete_username_validator])
    state = forms.ChoiceField(choices=(('registered', 'Préinscrit'), ('participant', 'Participant')))
    weight = forms.IntegerField(label='Pondération', min_value=0, required=True, initial=1)


class SharedEventDownloadXlsxForm(forms.Form):
    state = forms.ChoiceField(label='Selection',
                              choices=(('year', 'Listes de promotions'), ('registrants', 'Préinscrit'),
                                       ('participants', 'Participants')))

    def __init__(self, **kwargs):
        super(SharedEventDownloadXlsxForm, self).__init__(**kwargs)
        YEAR_CHOICES = []
        for year in list_year():
            YEAR_CHOICES.append(
                (year, year)
            )
        self.fields['years'] = forms.MultipleChoiceField(
            label='Année à inclure ',
            choices=YEAR_CHOICES,
            required=False
        )


class SharedEventUploadXlsxForm(forms.Form):
    list_user = forms.FileField(label='Fichier de données')
    state = forms.ChoiceField(
        label='Liste de ',
        choices=(('registrants', 'Préinscrits'), ('participants', 'Participants')))


class SetPriceProductBaseForm(forms.Form):
    is_manual = forms.BooleanField(label='Gestion manuelle du prix', required=False)
    manual_price = forms.DecimalField(label='Prix manuel', decimal_places=2, max_digits=9, min_value=0, required=False)
