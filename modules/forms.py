from django import forms

from modules.models import *
from shops.models import ProductBase
from users.models import User


class SelfSaleShopModule(forms.Form):
    def __init__(self, *args, **kwargs):
        module = kwargs.pop('module')
        super(SelfSaleShopModule, self).__init__(*args,**kwargs)

        for category in module.categories.all():
            for product in category.product_bases.all():
                self.fields[str(product.pk) + '-' + str(category.pk)] = forms.IntegerField(
                    label=product.sale_name(),
                    widget=forms.NumberInput(
                        attrs={'data_category_pk': category.pk,
                               'data_usual_price': product.get_moded_usual_price(),
                               'class': 'form-control',
                               'pk': product.pk}),
                    initial=0,
                    required=False
                )


class OperatorSaleShopModule(SelfSaleShopModule):
    client = forms.ChoiceField(
        label='Client',
        choices=([(None, 'Selectionner un client')] + [(str(user.pk)+'/'+str(user.balance), user.choice_string())
                 for user in User.objects.all().exclude(groups__pk=1)]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker',
                   'data-live-search': 'True'})
    )


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
            widget=forms.SelectMultiple(attrs={'class': 'selectpicker', 'data-live-search': 'True'}),
            required=False)


class ShopModuleConfigForm(forms.Form):
    state = forms.BooleanField(
        label='Etat',
        required=False
    )
