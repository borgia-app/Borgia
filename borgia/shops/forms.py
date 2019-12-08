from django import forms

from shops.models import Product, Shop


class ShopCreateForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'description', 'color']

    def clean(self):
        cleaned_data = super().clean()
        if Shop.objects.filter(name=cleaned_data.get('name')).exists():
            raise forms.ValidationError('Le code de magasin est déjà utilisé')


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
        super().__init__(**kwargs)
        self.fields['products'] = forms.ModelMultipleChoiceField(
            label='Produits',
            queryset=Product.objects.filter(shop=shop, is_removed=False),
            widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                               'data-live-search': 'True'}),
            required=False)


class ProductCreateForm(forms.ModelForm):
    on_quantity = forms.BooleanField(
        label='Produit vendu à la quantité',
        required=False)

    class Meta:
        model = Product
        fields = ['name', 'unit']

    def clean(self):
        cleaned_data = super().clean()
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
    search = forms.CharField(
        label='Recherche',
        max_length=255,
        required=False)
