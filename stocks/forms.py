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
                       'data-live-search': 'True'})
        )
    quantity = forms.IntegerField(
        label='En vente',
        required=False,
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input quantity',
                    'placeholder': 'Quantité',
                    'min':1}
        )
    )
    unit_quantity = forms.ChoiceField(
        label='Unité quantité',
        choices=([('UNIT', 'produits'), ('CL', 'cl'), ('L', 'L'), ('G', 'g'), ('KG', 'kg')]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker unit_quantity'}),
        required=False
    )
    amount = forms.DecimalField(
        label='Prix (€)',
        decimal_places=2,
        max_digits=9,
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input amount',
                    'placeholder': 'Montant',
                    'min':0}
        ))
    unit_amount = forms.ChoiceField(
        label='Unité montant',
        choices=([('UNIT', '€ / unité'), ('PACKAGE', '€ / lot'), ('L', '€ / L'), ('KG', '€ / kg')]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker unit_amount'}),
        required=False
    )

    def clean(self):
        cleaned_data = super(StockEntryProductForm, self).clean()
        # Validation direct in html
