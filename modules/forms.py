from django import forms
from django.core.exceptions import ObjectDoesNotExist

from modules.models import *
from shops.models import ProductBase
from users.models import User
from django.db.utils import OperationalError


class SelfSaleShopModule(forms.Form):
    def __init__(self, *args, **kwargs):
        module = kwargs.pop('module')
        self.client = kwargs.pop('client')
        super(SelfSaleShopModule, self).__init__(*args, **kwargs)

        for container_case in module.container_cases.all():
            self.fields[(
                str(container_case.pk)
                + '-'
                + 'container_cases')] = forms.IntegerField(
                label=container_case.product.product_base.sale_name(),
                widget=forms.NumberInput(
                    attrs={'data_category_pk': 'container_cases',
                           'data_container_case_name': container_case.name,
                           'data_usual_price': container_case.product.product_base.get_moded_usual_price(),
                           'class': 'form-control',
                           'pk': (
                               str(container_case.product.pk)
                               + '-'
                               + str(container_case.pk)
                               + '-cc')}),
                initial=0,
                required=False
            )

        for category in module.categories.all():
            for product in category.product_bases.all():
                if (product.quantity_products_stock() > 0
                        and product.get_moded_usual_price() > 0):
                    self.fields[(str(product.pk)
                                 + '-' + str(category.pk)
                                 )] = forms.IntegerField(
                        label=product.sale_name(),
                        widget=forms.NumberInput(
                            attrs={'data_category_pk': category.pk,
                                   'data_usual_price': product.get_moded_usual_price(),
                                   'class': 'form-control',
                                   'pk': (
                                       str(product.pk)
                                       + '-'
                                       + str(category.pk))}),
                        initial=0,
                        required=False
                    )

    def clean(self):
        cleaned_data = super(SelfSaleShopModule, self).clean()
        if self.client is None:
            try:
                self.client = User.objects.get(
                    pk=cleaned_data['client'].split('/')[0])
            except ObjectDoesNotExist:
                raise forms.ValidationError('Utilisateur inconnu')
        total_price = 0
        for field in cleaned_data:
            if field != 'client':
                invoice = cleaned_data[field]
                if invoice != 0 and isinstance(invoice, int):
                    product_pk = field.split('-')[0]
                    if 'container_cases' in field:
                        total_price += (
                            ContainerCase.objects.get(
                                pk=product_pk).product.product_base.get_moded_usual_price()
                            * invoice)
                    else:
                        total_price += (
                            ProductBase.objects.get(pk=product_pk).get_moded_usual_price()
                            * invoice)
        if total_price > self.client.balance:
            raise forms.ValidationError('Crédit insuffisant !')


class OperatorSaleShopModule(SelfSaleShopModule):
    try:
        client = forms.ChoiceField(
            label='Client',
            choices=([(None, 'Selectionner un client')] + [(str(user.pk)+'/'+str(user.balance), user.choice_string())
                     for user in User.objects.all().exclude(groups__pk=1)]),
            widget=forms.Select(
                attrs={'class': 'form-control selectpicker',
                       'data-live-search': 'True'})
        )
    except OperationalError:
        pass


class ModuleCategoryForm(forms.Form):
    name = forms.CharField(
        label='Nom',
        max_length=254
    )
    pk = forms.IntegerField(
        label='Pk',
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super(ModuleCategoryForm, self).__init__(*args, **kwargs)
        self.fields['products'] = forms.ModelMultipleChoiceField(
            label='Produits',
            queryset=ProductBase.objects.filter(shop=shop),
            widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                               'data-live-search': 'True'}),
            required=False)


class ShopModuleConfigForm(forms.Form):
    state = forms.BooleanField(
        label='Etat',
        required=False
    )


class ModuleContainerCaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super(ModuleContainerCaseForm, self).__init__(*args, **kwargs)
        self.fields['container_cases'] = forms.ModelMultipleChoiceField(
            label='Emplacements de vente',
            queryset=ContainerCase.objects.filter(shop=shop),
            widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                               'data-live-search': 'True'}),
            required=False)
