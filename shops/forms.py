#-*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import Textarea, PasswordInput
from django.db.models import Q
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

from shops.models import Shop, Container, ProductBase, ProductUnit
from users.models import User


class ReplacementActiveKegForm(forms.Form):

    new_keg = forms.ModelChoiceField(required=True,
                                     queryset=Container.objects.filter(quantity_remaining__isnull=False,
                                                                       product_base__product_unit__type='keg').exclude(
                                         place__contains='tireuse'),
                                     label='Nouveau fut')


class PurchaseAubergeForm(forms.Form):

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}))
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    # Client
    client_username = forms.CharField(label='Client', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}))

    def __init__(self, *args, **kwargs):

        # Initialisation des listes de produits
        container_meat_list = kwargs.pop('container_meat_list')
        container_cheese_list = kwargs.pop('container_cheese_list')
        container_side_list = kwargs.pop('container_side_list')
        single_product_available_list = kwargs.pop('single_product_available_list')
        self.request = kwargs.pop('request')
        super(PurchaseAubergeForm, self).__init__(*args, **kwargs)

        # Création des éléments de formulaire
        for (i, t) in enumerate(single_product_available_list):
            self.fields['field_single_product_%s' % i] = forms.IntegerField(required=True, min_value=0)
        for (i, t) in enumerate(container_meat_list):
            self.fields['field_container_meat_%s' % i] = forms.IntegerField(required=True, min_value=0)
        for (i, t) in enumerate(container_cheese_list):
            self.fields['field_container_cheese_%s' % i] = forms.IntegerField(required=True, min_value=0)
        for (i, t) in enumerate(container_side_list):
            self.fields['field_container_side_%s' % i] = forms.IntegerField(required=True, min_value=0)

    def single_product_avalaible_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_signle_product_'):
                yield (self.fields[name].label, value)

    def container_meat_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_container_meat_'):
                yield (self.fields[name].label, value)

    def container_cheese_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_container_cheese_'):
                yield (self.fields[name].label, value)

    def container_side_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_container_side_'):
                yield (self.fields[name].label, value)

    def clean(self):

        cleaned_data = super(PurchaseAubergeForm, self).clean()

        try:
            # Authentification de l'opérateur
            operator_username = cleaned_data['operator_username']
            operator_password = cleaned_data['operator_password']
            # Essaye d'authentification seulement si les deux champs sont valides
            if operator_password and operator_password:
                # Cas d'échec d'authentification
                operator = authenticate(username=operator_username, password=operator_password)
                if operator is not None:
                    if operator.has_perm('shops.sell_auberge') is False:
                        raise forms.ValidationError('Permission refusée !')
                else:
                    raise forms.ValidationError('Echec d\'authentification')

            # Validation de l'username
            client_username = cleaned_data['client_username']
            try:
                User.objects.get(username=client_username)
            except ObjectDoesNotExist:
                raise forms.ValidationError('Le client n\'existe pas')

            # Vérification de la commande sans provision
            if float(self.request.POST.get('hidden_balance_after')) < 0:
                raise forms.ValidationError('Commande sans provision')
        except KeyError:
            pass
        return super(PurchaseAubergeForm, self).clean()


class PurchaseFoyerForm(forms.Form):

    def __init__(self, *args, **kwargs):

        # Initialisation des listes de produits
        active_keg_container_list = kwargs.pop('active_keg_container_list')
        single_product_available_list = kwargs.pop('single_product_available_list')
        container_soft_list = kwargs.pop('container_soft_list')
        container_syrup_list = kwargs.pop('container_syrup_list')
        container_liquor_list = kwargs.pop('container_liquor_list')

        self.request = kwargs.pop('request')
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

    def clean(self):

        # Vérification de la commande sans provision
        if float(self.request.POST.get('hidden_balance_after')) < 0:
            raise forms.ValidationError('Commande sans provision')

        return super(PurchaseFoyerForm, self).clean()


class SingleProductCreateMultipleForm(forms.Form):

    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(SingleProductCreateMultipleForm, self).__init__(**kwargs)
        self.fields['product_base'] = forms.ModelChoiceField(label='Base produit',
                                                             queryset=ProductBase.objects.filter(type='single_product',
                                                                                                 shop=shop))
        self.fields['quantity'] = forms.IntegerField(label='Quantité à ajouter')
        self.fields['price'] = forms.FloatField(label='Prix d\'achat unitaire')
        self.fields['purchase_date'] = forms.DateField(label='Date d\'achat', widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['expiry_date'] = forms.DateField(label='Date d\'expiration', required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['place'] = forms.CharField(max_length=255, label='Lieu de stockage')


class ContainerCreateMultipleForm(forms.Form):

    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ContainerCreateMultipleForm, self).__init__(**kwargs)
        self.fields['product_base'] = forms.ModelChoiceField(label='Base produit',
                                                             queryset=ProductBase.objects.filter(type='container',
                                                                                                 shop=shop).exclude(
                                                                 product_unit__type='fictional_money'))
        self.fields['quantity'] = forms.IntegerField(label='Quantité à ajouter')
        self.fields['price'] = forms.FloatField(label='Prix d\'achat unitaire')
        self.fields['purchase_date'] = forms.DateField(label='Date d\'achat', widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['expiry_date'] = forms.DateField(label='Date d\'expiration', required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['place'] = forms.CharField(max_length=255, label='Lieu de stockage')


class ProductCreateMultipleForm(forms.Form):

    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ProductCreateMultipleForm, self).__init__(**kwargs)
        self.fields['product_base'] = forms.ModelChoiceField(label='Base produit',
                                                             queryset=ProductBase.objects.filter(shop=shop).exclude(
                                                                 product_unit__type='fictional_money'))
        self.fields['quantity'] = forms.IntegerField(label='Quantité à ajouter')
        self.fields['price'] = forms.FloatField(label='Prix d\'achat unitaire')
        self.fields['purchase_date'] = forms.DateField(label='Date d\'achat', widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['expiry_date'] = forms.DateField(label='Date d\'expiration', required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['place'] = forms.CharField(max_length=255, label='Lieu de stockage')


class ProductBaseListPriceForm(forms.Form):
    shop = forms.ModelChoiceField(label='Magasin', queryset=Shop.objects.all(), empty_label=None)