from django import forms
from django.forms.formsets import BaseFormSet

from shops.models import Product, Shop


class StockEntryProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super().__init__(*args, **kwargs)
        product_choice = ([(None, 'Sélectionner un produit')] +
                          [(str(product.pk)+'/'+str(product.get_unit_display()), product.__str__())
                           for product in Product.objects.filter(shop=shop, is_removed=False)]
                          )
        self.fields['product'].choices = product_choice

    product = forms.ChoiceField(label='Produit', widget=forms.Select(
        attrs={'class': 'form-control selectpicker',
               'data-live-search': 'True', 'required': 'required'}))

    quantity = forms.IntegerField(
        label='En vente',
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input quantity',
                   'placeholder': 'Quantité',
                   'min': 1, 'required': 'required'}),
        required=False
    )
    unit_quantity = forms.ChoiceField(
        label='Unité quantité',
        choices=([('UNIT', 'produits'), ('CL', 'cl'),
                  ('L', 'L'), ('G', 'g'), ('KG', 'kg')]),
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
                   'min': 0, 'required': 'required'})
    )
    unit_amount = forms.ChoiceField(
        label='Unité montant',
        choices=([('UNIT', '€ / unité'), ('PACKAGE', '€ / lot'),
                  ('L', '€ / L'), ('KG', '€ / kg')]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker unit_amount', 'required': 'required'}),
        required=False
    )
    inventory_quantity = forms.IntegerField(
        label='Stocks restant',
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input quantity',
                   'placeholder': 'Stocks rest.',
                   'min': 0}),
        required=False
    )
    unit_inventory = forms.ChoiceField(
        label='Unité quantité',
        choices=([('UNIT', 'produits'), ('CL', 'cl'),
                  ('L', 'L'), ('G', 'g'), ('KG', 'kg')]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker unit_quantity'}),
        required=False
    )

    # TODO : Validation


class BaseInventoryProductFormSet(BaseFormSet):
    def clean(self):
        """
        Check that there is max one inventory for each product
        """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        products = []
        for form in self.forms:
            product = form.cleaned_data['product'].split('/')[0]

            if product in products:
                raise forms.ValidationError(
                    "Impossible de définir deux produits identiques dans le même inventaire")
            products.append(product)


class AdditionnalDataStockEntryForm(forms.Form):
    isAddingInventory = forms.ChoiceField(label='Faire également un inventaire des stocks',
                                          choices=([('with', 'Avec'), ('without', 'Sans')]))


class StockEntryListDateForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super().__init__(**kwargs)
        if shop is None:
            self.fields['shop'] = forms.ModelChoiceField(
                label='Magasin',
                queryset=Shop.objects.all(),
                empty_label='Tous',
                required=False
            )
    date_begin = forms.DateField(
        label='Date de début',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False
    )
    date_end = forms.DateField(
        label='Date de fin',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False
    )


class AdditionnalDataInventoryForm(forms.Form):
    type = forms.ChoiceField(label='Type d\'Inventaire',
                             choices=([('partial', 'Partiel'), ('full', 'Complet')]))


class InventoryProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super().__init__(*args, **kwargs)

        product_choice = ([(None, 'Sélectionner un produit')] +
                          [(str(product.pk)+'/'+str(product.get_unit_display()), product.__str__())
                           for product in Product.objects.filter(shop=shop, is_removed=False)]
                          )
        self.fields['product'].choices = product_choice

    product = forms.ChoiceField(label='Produit', widget=forms.Select(
        attrs={'class': 'form-control selectpicker',
               'data-live-search': 'True', 'required': 'required'}))
    quantity = forms.IntegerField(
        label='En vente',
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input quantity',
                   'placeholder': 'Quantité',
                   'min': 0, 'required': 'required'}),
        required=False
    )
    unit_quantity = forms.ChoiceField(
        label='Unité quantité',
        choices=([('UNIT', 'produits'), ('CL', 'cl'),
                  ('L', 'L'), ('G', 'g'), ('KG', 'kg')]),
        widget=forms.Select(
            attrs={'class': 'form-control selectpicker unit_quantity', 'required': 'required'}),
        required=False
    )

    # TODO : Validation


class InventoryListDateForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super().__init__(**kwargs)
        if shop is None:
            self.fields['shop'] = forms.ModelChoiceField(
                label='Magasin',
                queryset=Shop.objects.all(),
                empty_label='Tous',
                required=False
            )
    date_begin = forms.DateField(
        label='Date de début',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False
    )
    date_end = forms.DateField(
        label='Date de fin',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False
    )
