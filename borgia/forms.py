#-*- coding: utf-8 -*-

from django import forms
from django.forms import Form
from django.forms.widgets import PasswordInput


class LoginFoyerForm(Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255, widget=PasswordInput)