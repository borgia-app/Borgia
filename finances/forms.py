import re
import datetime

from django import forms
from django.contrib.auth import authenticate
from django.forms.widgets import PasswordInput
from django.core.validators import RegexValidator
from django.contrib.auth.models import Permission

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


class SelfTransfertCreateForm(forms.Form):
    def __init__(self, **kwargs):
        self.sender = kwargs.pop('sender')
        super(SelfTransfertCreateForm, self).__init__(**kwargs)

        self.fields['recipient'] = forms.CharField(
    		label="Receveur",
            max_length=255,
            required=True,
            widget=forms.TextInput(attrs={'class': 'form-control autocomplete_username',
                                          'autocomplete': 'off',
    									  'autofocus': 'true',
    									  'placeholder': "Nom d'utilisateur"}))
        self.fields['amount'] = forms.DecimalField(
            label='Montant (€)',
            decimal_places=2,
            max_digits=9,
            min_value=0, max_value=self.sender.balance)
        self.fields['justification'] = forms.CharField(
            label='Justification',
            max_length=254
        )

    def clean_recipient(self):
        username = self.cleaned_data['recipient']

        try:
            recipient = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError("L'utilisateur n'existe pas !")

        if not recipient.is_active:
            raise forms.ValidationError("L'utilisateur a été supprimé !")

        if self.sender == recipient:
            # Send to self : Impossible
            raise forms.ValidationError("Vous ne pouvez pas transferez à vous même !")

        return recipient


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
        self.fields['amount'] = forms.DecimalField(
            label='Montant (€)',
            decimal_places=2, max_digits=9,
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
    type_payment = forms.ChoiceField(label='Type', choices=(('pay_by_total', 'Payer par division du total'),
                                                        ('pay_by_ponderation', 'Payer par prix par pondération'),
                                                        ('no_payment', 'Ne pas faire payer')))
    total_price = forms.DecimalField(label='Prix total', decimal_places=2, max_digits=9,
                                   required=False, min_value=0.01)
    ponderation_price = forms.DecimalField(label='Prix par pondération', decimal_places=2, max_digits=9,
                                   required=False, min_value=0.01)
    remark = forms.CharField(label='Pourquoi finir l\'événement ?', required=False)

    def clean_total_price(self):
        data = self.cleaned_data['total_price']

        if self.cleaned_data['type_payment'] == 'pay_by_total':
            if data is None:
                raise forms.ValidationError('Obligatoire !')

        return data

    def clean_ponderation_price(self):
        data = self.cleaned_data['ponderation_price']

        if self.cleaned_data['type_payment'] == 'pay_by_ponderation':
            if data is None:
                raise forms.ValidationError('Obligatoire !')

        return data

    def clean_remark(self):
        data = self.cleaned_data['remark']

        if self.cleaned_data['type_payment'] == 'no_payment':
            if not data:
                raise forms.ValidationError('Obligatoire !')

        return data


class SharedEventUpdateForm(forms.Form):
    price = forms.DecimalField(label='Prix total (€)', decimal_places=2, max_digits=9, min_value=0, required=False)
    bills = forms.CharField(label='Factures liées', required=False)
    allow_self_registeration = forms.BooleanField(label='Autoriser la préinscription', required=False)


class SharedEventListUsersForm(forms.Form):
    order_by = forms.ChoiceField(label='Trier par', choices=(('username', 'Username'), ('last_name', 'Nom'), ('surname', 'Bucque'), ('year', 'Promo')))
    state = forms.ChoiceField(label='Lister', choices=(('users', 'Tous les concernés'),
                                                ('registrants', 'Uniquement les préinscrits'),
                                                ('participants', 'Uniquement les participants')))


class SharedEventSelfRegistrationForm(forms.Form):
    weight = forms.IntegerField(label='Pondération', min_value=0)


class SharedEventAddWeightForm(forms.Form):
    user = forms.CharField(
    		label="Ajouter",
            max_length=255,
            required=True,
            widget=forms.TextInput(attrs={'class': 'form-control autocomplete_username',
                                          'autocomplete': 'off',
    									  'autofocus': 'true',
    									  'placeholder': "Nom d'utilisateur"}))

    state = forms.ChoiceField(label='En tant que', choices=(('registered', 'Préinscrit'), ('participant', 'Participant')))
    weight = forms.IntegerField(label='Pondération', min_value=0, required=True, initial=1)

    def clean_user(self):
        username = self.cleaned_data['user']

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError("L'utilisateur n'existe pas !")

        if not user.is_active :
            raise forms.ValidationError("L'utilisateur a été supprimé !")

        return user


class SharedEventDownloadXlsxForm(forms.Form):
    state = forms.ChoiceField(label='Selection',
                              choices=(('year', 'Listes de promotions'), ('registrants', 'Préinscrit'),
                                       ('participants', 'Participants')))
    years = forms.MultipleChoiceField(label='Année(s) à inclure', required=False)

    def __init__(self, **kwargs):
        super(SharedEventDownloadXlsxForm, self).__init__(**kwargs)
        YEAR_CHOICES = []
        for year in list_year():
            YEAR_CHOICES.append(
                (year, year)
            )
        self.fields['years'].choices = YEAR_CHOICES


class SharedEventUploadXlsxForm(forms.Form):
    list_user = forms.FileField(label='Fichier de données')
    state = forms.ChoiceField(
        label='Liste de ',
        choices=(('registrants', 'Préinscrits'), ('participants', 'Participants')))


class SetPriceProductBaseForm(forms.Form):
    is_manual = forms.BooleanField(label='Gestion manuelle du prix', required=False)
    manual_price = forms.DecimalField(label='Prix manuel', decimal_places=2, max_digits=9, min_value=0, required=False)
