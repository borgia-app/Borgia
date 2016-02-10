#-*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import Textarea
from django.db.models import Q

from shops.models import Shop, SingleProduct, Container


class PurchaseFoyerForm(forms.Form):

    def __init__(self, *args, **kwargs):
        tap_list = kwargs.pop('tap_list')
        single_product_list = kwargs.pop('single_product_list')
        single_product_list_qt = kwargs.pop('single_product_list_qt')
        product_unit_soft_list = kwargs.pop('product_unit_soft_list')
        product_unit_liquor_list = kwargs.pop('product_unit_liquor_list')

        super(PurchaseFoyerForm, self).__init__(*args, **kwargs)

        for (i, t) in enumerate(tap_list):
            self.fields['field_tap_%s' % i] = forms.IntegerField(required=True, min_value=0)

        # TODO: problème si on prend exactement tout ce qu'il reste ...
        for (i, t) in enumerate(single_product_list):
            self.fields['field_single_product_%s' % i] = forms.IntegerField(required=True, min_value=0,
                                                                            max_value=single_product_list_qt[i])

        for (i, t) in enumerate(product_unit_soft_list):
            self.fields['field_product_unit_soft_%s' % i] = forms.IntegerField(required=True, min_value=0)

        for (i, t) in enumerate(product_unit_liquor_list):
            self.fields['field_product_unit_liquor_%s' % i] = forms.IntegerField(required=True, min_value=0)

    def tap_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_tap_'):
                yield (self.fields[name].label, value)

    def single_product_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_single_product_'):
                yield (self.fields[name].label, value)

    def product_unit_soft_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_product_unit_soft_'):
                yield (self.fields[name].label, value)

    def product_unit_liquor_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_product_unit_liquor_'):
                yield (self.fields[name].label, value)


class SingleProductCreateMultipleForm(forms.Form):

    quantity = forms.IntegerField()
    price = forms.FloatField()

    def __init__(self, *args, **kwargs):
        single_product_list = kwargs.pop('single_product_list')
        single_product_pk_list = []
        for e in single_product_list:
            single_product_pk_list.append(e.pk)

        super(SingleProductCreateMultipleForm, self).__init__(*args, **kwargs)
        self.fields['single_product'] = forms.ModelChoiceField(
                queryset=SingleProduct.objects.filter(pk__in=single_product_pk_list))


class ContainerCreateMultipleForm(forms.Form):

    quantity = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        container_list = kwargs.pop('container_list')
        container_pk_list = []
        for e in container_list:
            container_pk_list.append(e.pk)

        super(ContainerCreateMultipleForm, self).__init__(*args, **kwargs)
        self.fields['container'] = forms.ModelChoiceField(
                queryset=Container.objects.filter(pk__in=container_pk_list))