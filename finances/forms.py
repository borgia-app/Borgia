#-*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.forms import ModelForm
from django.forms.widgets import PasswordInput

from users.models import User
from finances.models import Cheque, Cash, Lydia, BankAccount


class ChequeCreateForm(ModelForm):
    class Meta:
        model = Cheque
        fields = ['amount', 'is_cashed', 'signature_date', 'cheque_number', 'sender', 'bank_account', 'recipient']

    bank_account = forms.ModelChoiceField(label='Compte en banque', queryset=BankAccount.objects.all())


class CreationLydiaForm(ModelForm):
    class Meta:
        model = Lydia
        fields = ['sender_user_id', 'recipient_user_id', 'date_operation', 'time_operation', 'id_from_lydia', 'amount', 'banked', 'date_banked']

    sender_user_id = forms.ModelChoiceField(label='Impulseur', queryset=User.objects.all().order_by('last_name'))
    recipient_user_id = forms.ModelChoiceField(label='Destinataire', queryset=User.objects.all().order_by('last_name'))


class CreationCashForm(ModelForm):
    class Meta:
        model = Cash
        fields = ['giver', 'amount']

    giver = forms.ModelChoiceField(label='Donnateur', queryset=User.objects.all().order_by('last_name'))


class SupplyChequeForm(forms.Form):

    # Chèque
    amount = forms.FloatField(label='Montant')
    sender = forms.ModelChoiceField(label='Payeur', queryset=User.objects.all())
    bank_account = forms.ModelChoiceField(label='Compte bancaire', queryset=BankAccount.objects.all())
    cheque_number = forms.CharField(label='Numéro unique', max_length=7)
    signature_date = forms.DateField(label='Date de signature')

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire')
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    def clean(self):

        cleaned_data = super(SupplyChequeForm, self).clean()
        operator_username = cleaned_data['operator_username']
        operator_password = cleaned_data['operator_password']

        # Essaye d'authentification seulement si les deux champs sont valides
        if operator_password and operator_password:
            # Cas d'échec d'authentification
            if authenticate(username=operator_username, password=operator_password) is None:
                raise forms.ValidationError('Echec d\'authentification')
        return super(SupplyChequeForm, self).clean()
