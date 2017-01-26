from django import forms

from django.contrib.admin.widgets import FilteredSelectMultiple

from modules.models import *
from shops.models import ProductBase


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
