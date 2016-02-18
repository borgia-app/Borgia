#-*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import Textarea
from django.db.models import Q

from shops.models import Shop, Container, ProductBase


class ReplacementActiveKegForm(forms.Form):

    new_keg = forms.ModelChoiceField(required=True,
                                     queryset=Container.objects.filter(product_base__shop=Shop.objects.get(name='Foyer'),
                                                                       quantity_remaining__isnull=False,
                                                                       product_base__product_unit__type='keg').exclude(
                                             place__contains='tireuse'),
                                     label='Nouveau fut')


class PurchaseFoyerForm(forms.Form):

    def __init__(self, *args, **kwargs):

        # Initialisation des listes de produits
        active_keg_container_list = kwargs.pop('active_keg_container_list')
        single_product_available_list = kwargs.pop('single_product_available_list')
        container_soft_list = kwargs.pop('container_soft_list')
        container_syrup_list = kwargs.pop('container_syrup_list')
        container_liquor_list = kwargs.pop('container_liquor_list')
        super(PurchaseFoyerForm, self).__init__(*args, **kwargs)

        # Création des éléments de formulaire
        for (i, t) in enumerate(active_keg_container_list):
            self.fields['field_active_keg_container_%s' % i] = forms.IntegerField(required=True, min_value=0)
        for (i, t) in enumerate(single_product_available_list):
            self.fields['field_single_product_%s' % i] = forms.IntegerField(required=True, min_value=0,
                                                                            max_value=len(t[1]))
        for (i, t) in enumerate(container_soft_list):
            self.fields['field_container_soft_%s' % i] = forms.IntegerField(required=True, min_value=0)
        for (i, t) in enumerate(container_syrup_list):
            self.fields['field_container_syrup_%s' % i] = forms.IntegerField(required=True, min_value=0)
        for (i, t) in enumerate(container_liquor_list):
            self.fields['field_container_liquor_%s' % i] = forms.IntegerField(required=True, min_value=0)

    # Fonctions de récupérations des réponses en POST
    def active_keg_container_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_active_keg_container_'):
                yield (self.fields[name].label, value)

    def single_product_available_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_single_product_'):
                yield (self.fields[name].label, value)

    def container_soft_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_container_soft_'):
                yield (self.fields[name].label, value)

    def container_syrup_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_container_syrup_'):
                yield (self.fields[name].label, value)

    def container_liquor_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_container_liquor_'):
                yield (self.fields[name].label, value)


class SingleProductCreateMultipleForm(forms.Form):

    product_base = forms.ModelChoiceField(label='Base produit',
                                          queryset=ProductBase.objects.filter(type='single_product'))
    quantity = forms.IntegerField(label='Quantité à ajouter')
    price = forms.FloatField(label='Prix d\'achat unitaire')
    purchase_date = forms.DateField(label='Date d\'achat')
    expiry_date = forms.DateField(label='Date d\'expiration', required=False)
    place = forms.CharField(max_length=255, label='Lieu de stockage')


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