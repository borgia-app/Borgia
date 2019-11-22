import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.forms.widgets import PasswordInput

from borgia.validators import autocomplete_username_validator
from users.models import User


class TransfertCreateForm(forms.Form):
    def __init__(self, **kwargs):
        self.sender = kwargs.pop('sender')
        super().__init__(**kwargs)

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
            min_value=0, max_value=max(self.sender.balance, 0))
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
            raise forms.ValidationError("L'utilisateur a été desactivé !")
        if self.sender == recipient:
            # Send to self : Impossible
            raise forms.ValidationError(
                "Vous ne pouvez pas transferez à vous même !")

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


class RechargingListForm(GenericListSearchDateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            perm = Permission.objects.get(codename='add_recharging')
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
        cleaned_data = super().clean()

        try:
            operator_username = cleaned_data['operator_username']
            operator_password = cleaned_data['operator_password']
            if (authenticate(
                    username=operator_username,
                    password=operator_password) is None):
                raise forms.ValidationError('Echec d\'authentification')
        except KeyError:
            pass

        return super().clean()


class RechargingCreateForm(forms.Form):
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
        super().__init__(**kwargs)

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

    def clean(self):

        cleaned_data = super().clean()

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
        super().__init__(**kwargs)
        self.fields['recharging_amount'] = forms.DecimalField(
            label='Montant à recharger (€)',
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


class SetPriceProductBaseForm(forms.Form):
    is_manual = forms.BooleanField(
        label='Gestion manuelle du prix', required=False)
    manual_price = forms.DecimalField(
        label='Prix manuel', decimal_places=2, max_digits=9, min_value=0, required=False)
