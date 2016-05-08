#-*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import Textarea, PasswordInput
from django.db.models import Q
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import ModelChoiceField

from shops.models import Shop, Container, ProductBase, ProductUnit
from users.models import User
from django.contrib.auth.models import Group
from borgia.validators import autocomplete_username_validator


class ReplacementActiveKegForm(forms.Form):

    """
    Sont proposés les produits de base seulement (pour ne pas avoir à scroller s'il y a 20 fûts d'un produit ...)
    Seuls les produits de base dont l'unité concene un fût,
    pour les produits de base dont un fût est sous une tireuse : au moins 2 fûts dispo (un sous et un autre en stock)
    pour les autres au moins 1 fût dispo (en stock)
    """

    def __init__(self, *args, **kwargs):
        list_active_keg = kwargs.pop('list_active_keg')
        super(ReplacementActiveKegForm, self).__init__(*args, **kwargs)

        query = ProductBase.objects.filter(product_unit__type='keg')
        for keg_base in query:
            list_container_from_keg_base = Container.objects.filter(product_base=keg_base, is_sold=False)

            # Si un seul conteneur existe, on vérifie que ce n'est pas celui sous la tireuse
            if list_container_from_keg_base.count() == 1:
                for active_keg in list_active_keg:
                    if active_keg in list_container_from_keg_base:
                        query = query.exclude(pk=keg_base.pk)
            # Si aucun conteneur existe, le produit de base n'est pas proposé
            elif list_container_from_keg_base.count() == 0:
                query = query.exclude(pk=keg_base.pk)

        # Ajout du conteneur "vide" via la définition du ModelChoice
        self.fields['new_keg_product_base'] = ModelChoiceFieldWithQuantity(label='Nouveau fût', queryset=query,
                                                                           list_active_keg=list_active_keg,
                                                                           empty_label='Tireuse vide',
                                                                           required=False)
        self.fields['is_sold'] = forms.BooleanField(required=False, label='L\'ancien fût est vide')


class ModelChoiceFieldWithQuantity(ModelChoiceField):
    """
    Override d'un ModelChoiceField en ajoutant la quantité de conteneurs disponibles (sans celui sous la tireuse)
    dans le nom du produit de base
    """
    def __init__(self, **kwargs):
        self.list_active_keg = kwargs.pop('list_active_keg')
        super(ModelChoiceFieldWithQuantity, self).__init__(**kwargs)

    def label_from_instance(self, obj):
        list_container = Container.objects.filter(product_base=obj, is_sold=False)
        quantity_in_stock = list_container.count()
        for cont in self.list_active_keg:
            if cont in list_container:
                quantity_in_stock -= 1
                
        return obj.__str__() + ' (' + str(quantity_in_stock) + ')'


class PurchaseAubergeForm(forms.Form):

    # Gestionnaire - opérateur
    operator_username = forms.CharField(label='Gestionnaire',
                                        widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                                        validators=[autocomplete_username_validator])
    operator_password = forms.CharField(label='Mot de passe', widget=PasswordInput)

    # Client
    client_username = forms.CharField(label='Client', widget=forms.TextInput(attrs={'class': 'autocomplete_username'}),
                                      validators=[autocomplete_username_validator])

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
            # Cas d'échec d'authentification
            operator = authenticate(username=operator_username, password=operator_password)
            if operator is not None:
                if operator.has_perm('shops.sell_auberge') is False:
                    raise forms.ValidationError('Permission refusée !')
            else:
                raise forms.ValidationError('Echec d\'authentification')

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
            self.fields['field_container_entire_liquor_%s' % i] = forms.IntegerField(required=True, min_value=0)

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

    def container_entire_liquor_answers(self):
        for name, value in self.cleaned_data.items():
            if name.startwith('field_container_entire_liquor_'):
                yield (self.fields[name].label, value)

    def clean(self):
        try:
            # Vérification de la commande sans provision
            if float(self.request.POST.get('hidden_balance_after')) < 0:
                raise forms.ValidationError('Commande sans provision')
        except ValueError:
            raise forms.ValidationError('Erreur, veuillez recharger la page (F5 dans la barre d\'url)')

        return super(PurchaseFoyerForm, self).clean()


class ProductCreateMultipleForm(forms.Form):

    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ProductCreateMultipleForm, self).__init__(**kwargs)
        self.fields['product_base'] = forms.ModelChoiceField(label='Base produit',
                                                             queryset=ProductBase.objects.filter(shop=shop).exclude(
                                                                 product_unit__type='fictional_money'))
        self.fields['quantity'] = forms.IntegerField(label='Quantité à ajouter', min_value=0)
        self.fields['price'] = forms.DecimalField(label='Prix d\'achat unitaire', decimal_places=2, max_digits=9,
                                                  min_value=0)
        self.fields['purchase_date'] = forms.DateField(label='Date d\'achat',
                                                       widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['expiry_date'] = forms.DateField(label='Date d\'expiration', required=False,
                                                     widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['place'] = forms.CharField(max_length=255, label='Lieu de stockage')


class ProductListForm(forms.Form):
    def __init__(self, **kwargs):
        user = kwargs.pop('request').user
        super(ProductListForm, self).__init__(**kwargs)

        if Group.objects.get(name='Trésoriers') in user.groups.all():
            self.fields['shop'] = forms.ModelChoiceField(label='Magasin',
                                                         queryset=Shop.objects.all(),
                                                         empty_label=None)
        else:
            available_shop = []
            if user.has_perm('shops.list_productbase'):
                if Group.objects.get(name='Chefs gestionnaires du foyer') in user.groups.all() or Group.objects.get(name='Gestionnaires du foyer') in user.groups.all():
                    available_shop.append(Shop.objects.get(name='Foyer').pk)
                if Group.objects.get(name='Chefs gestionnaires de l\'auberge') in user.groups.all() or Group.objects.get(name='Gestionnaires de l\'auberge') in user.groups.all():
                    available_shop.append(Shop.objects.get(name='Auberge').pk)

            self.fields['shop'] = forms.ModelChoiceField(label='Magasin', queryset=Shop.objects.filter(pk__in=available_shop), empty_label=None)

        choices_type_product = []
        choices_type_product.append(('product_base', 'Bases de produits'))
        if user.has_perm('shops.list_productunit'):
            choices_type_product.append(('product_unit', 'Unités de produits'))
        self.fields['type_product'] = forms.ChoiceField(label='Type de produits', choices=choices_type_product)
