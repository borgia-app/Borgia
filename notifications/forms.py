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


class notiftest(forms.Form):
    recipient = forms.CharField(label='Receveur', max_length=255,
                                widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                                validators=[autocomplete_username_validator])

    amount = forms.DecimalField(label='Montant (€)', decimal_places=2, max_digits=9, min_value=0)
