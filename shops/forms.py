#-*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.forms import ModelForm
from django.forms.widgets import PasswordInput


class PurchaseFoyerForm(forms.Form):

    def __init__(self, *args, **kwargs):
        tap_list = kwargs.pop('tap_list')
        single_product_list = kwargs.pop('single_product_list')
        product_unit_other = kwargs.pop('product_unit_other_list')

        super(PurchaseFoyerForm, self).__init__(*args, **kwargs)

        for (i, t) in enumerate(tap_list):
            self.fields['field_tap_%s' % i] = forms.IntegerField(required=True, min_value=0)

        for (i, t) in enumerate(single_product_list):
            self.fields['field_single_product_%s' % i] = forms.IntegerField(required=True, min_value=0)

        for (i, t) in enumerate(product_unit_other):
            self.fields['field_product_unit_other_%s' % i] = forms.IntegerField(required=True, min_value=0)

    def tap_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_tap_'):
                yield (self.fields[name].label, value)

    def single_product_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_single_product_'):
                yield (self.fields[name].label, value)

    def product_unit_other_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_product_unit_other_'):
                yield (self.fields[name].label, value)
