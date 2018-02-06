from django import forms

from shops.models import Shop, Product


class StockEntryProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super(StockEntryProductForm, self).__init__(*args, **kwargs)
        self.fields['product'] = forms.ChoiceField(
            label='Produit',
            choices=([(None, 'Sélectionner un produit')] + [(str(product.pk)+'/'+str(product.get_unit_display()), product.__str__())
                     for product in Product.objects.filter(shop=shop)]),
            widget=forms.Select(
                attrs={'class': 'form-control selectpicker',
                       'data-live-search': 'True', 'required':'required'})
        )
    quantity = forms.IntegerField(
        label='En vente',
        required=False,
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input quantity',
                    'placeholder': 'Quantité',
                    'min':1, 'required':'required'}
        )
    )
    unit_quantity = forms.ChoiceField(
        label='Unité quantité',
        choices=([('UNIT', 'produits'), ('CL', 'cl'), ('L', 'L'), ('G', 'g'), ('KG', 'kg')]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker unit_quantity', 'required': 'required'}),
        required=False
    )
    amount = forms.DecimalField(
        label='Prix (€)',
        decimal_places=2,
        max_digits=9,
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input amount',
                    'placeholder': 'Montant',
                    'min':0, 'required':'required'}
        ))
    unit_amount = forms.ChoiceField(
        label='Unité montant',
        choices=([('UNIT', '€ / unité'), ('PACKAGE', '€ / lot'), ('L', '€ / L'), ('KG', '€ / kg')]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker unit_amount', 'required':'required'}),
        required=False
    )

    def clean(self):
        cleaned_data = super(StockEntryProductForm, self).clean()
        # Validation direct in html


class StockEntryListDateForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(StockEntryListDateForm, self).__init__(**kwargs)
        if shop is None:
            self.fields['shop'] = forms.ModelChoiceField(
                label='Magasin',
                queryset=Shop.objects.all().exclude(pk=1),
                empty_label='Tous',
                required=False
            )
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


class InventoryProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super(InventoryProductForm, self).__init__(*args, **kwargs)
        self.fields['product'] = forms.ChoiceField(
            label='Produit',
            choices=([(None, 'Sélectionner un produit')] + [(str(product.pk)+'/'+str(product.get_unit_display()), product.__str__())
                     for product in Product.objects.filter(shop=shop)]),
            widget=forms.Select(
                attrs={'class': 'form-control selectpicker',
                       'data-live-search': 'True', 'required':'required'})
        )
    quantity = forms.IntegerField(
        label='En vente',
        required=False,
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input quantity',
                    'placeholder': 'Quantité',
                    'min':0, 'required':'required'}
        )
    )
    unit_quantity = forms.ChoiceField(
        label='Unité quantité',
        choices=([('UNIT', 'produits'), ('CL', 'cl'), ('L', 'L'), ('G', 'g'), ('KG', 'kg')]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker unit_quantity', 'required': 'required'}),
        required=False
    )

    def clean(self):
        cleaned_data = super(InventoryProductForm, self).clean()
        # Validation direct in html



class InventoryListDateForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(InventoryListDateForm, self).__init__(**kwargs)
        if shop is None:
            self.fields['shop'] = forms.ModelChoiceField(
                label='Magasin',
                queryset=Shop.objects.all().exclude(pk=1),
                empty_label='Tous',
                required=False
            )
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
