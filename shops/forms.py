from django import forms
from django.forms.models import ModelChoiceField

from shops.models import Shop, Product
from borgia.validators import autocomplete_username_validator


class ProductCreateForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ProductCreateForm, self).__init__(**kwargs)
        if shop is None:
            self.fields['shop'] = forms.ModelChoiceField(
                label='Magasin',
                queryset=Shop.objects.all().exclude(pk=1)
            )
        self.fields['name'] = forms.CharField(
            label='Nom',
            max_length=254
        )
        self.fields['on_quantity'] = forms.BooleanField(
            label='Produit vendu à la quantité',
            required=False)
        self.fields['unit'] = forms.ChoiceField(
            label='Unité de vente',
            choices=(('CL', 'cl'), ('G', 'g')),
            required=False)


    def clean(self):
        cleaned_data = super(ProductCreateForm, self).clean()
        on_quantity = cleaned_data.get('on_quantity')
        unit = cleaned_data.get('unit')
        if on_quantity:
            if unit is None:
                raise forms.ValidationError(
                    'Une unité de vente est nécessaire pour un produit en vente à la quantité'
                )


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name']


class ProductUpdatePriceForm(forms.Form):
    is_manual = forms.BooleanField(
        label='Gestion manuelle du prix', required=False)
    manual_price = forms.DecimalField(label='Prix manuel',
                                      decimal_places=2,
                                      max_digits=9, min_value=0,
                                      required=False)


class ProductListForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ProductListForm, self).__init__(**kwargs)
        if shop is None:
            self.fields['shop'] = forms.ModelChoiceField(
                label='Magasin',
                queryset=Shop.objects.all().exclude(pk=1),
                required=False
            )
        self.fields['search'] = forms.CharField(
            label='Recherche',
            max_length=255,
            required=False)


class ShopCreateForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'description', 'color']


class ShopUpdateForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['description', 'color']


class ShopCheckupSearchForm(forms.Form):
    date_begin = forms.DateField(
        label='Date de début',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False)
    date_end = forms.DateField(
        label='Date de fin',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False)

    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ShopCheckupSearchForm, self).__init__(**kwargs)
        self.fields['products'] = forms.ModelMultipleChoiceField(
            label='Produits',
            queryset=ProductBase.objects.filter(shop=shop),
            widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                               'data-live-search': 'True'}),
            required=False)
