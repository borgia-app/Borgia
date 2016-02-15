#-*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.forms import ModelForm
from django.forms.widgets import PasswordInput

from users.models import User
from finances.models import Cheque, Cash, Lydia


class CreationChequeForm(ModelForm):
    class Meta:
        model = Cheque
        fields = ['signatory', 'recipient', 'date_sign', 'amount', 'number']

    signatory = forms.ModelChoiceField(label='Signataire', queryset=User.objects.all().order_by('last_name'))
    recipient = forms.ModelChoiceField(label='Ordre', queryset=User.objects.all().order_by('last_name'))


class CreationLydiaForm(ModelForm):
    class Meta:
        model = Lydia
        fields = ['giver', 'receiver', 'date_operation', 'time_operation', 'amount']

    giver = forms.ModelChoiceField(label='Donnateur', queryset=User.objects.all().order_by('last_name'))
    receiver = forms.ModelChoiceField(label='Receveur', queryset=User.objects.all().order_by('last_name'))


class CreationCashForm(ModelForm):
    class Meta:
        model = Cash
        fields = ['giver', 'amount']

    giver = forms.ModelChoiceField(label='Donnateur', queryset=User.objects.all().order_by('last_name'))


# Classe mère transaction rapide
class CreationTransactionPaymentFast(forms.Form):
    # Champs d'authentification
    operator = forms.ModelChoiceField(label='Opérateur',
                                      queryset=User.objects.filter(groups__name='Gestionnaires du foyer'))
    password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    # Payement
    amount = forms.FloatField(label='Montant en euros')

    # Création de la transaction
    client = forms.ModelChoiceField(label='Client', queryset=User.objects.all().order_by('last_name'))


# Classe fille transaction rapide chèque
class CreationTransactionChequeFastForm(CreationTransactionPaymentFast):
    # Création du chèque
    number = forms.CharField(label='Numéro unique', max_length=7)


# Classe fille transaction rapide lydia
class CreationTransactionLydiaFastForm(CreationTransactionPaymentFast):
    # Création du virement lydia
    time_operation = forms.TimeField(label='Heure du virement Lydia')