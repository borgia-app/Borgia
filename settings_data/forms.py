from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class PriceConfigForm(forms.Form):
    margin_profit = forms.DecimalField(label='Marge appliquée aux prix en mode automatique',
                                        decimal_places=2, max_digits=9,
                                        validators=[
                                          MinValueValidator(0, 'Le montant doit être positif')],
                                        required=False)


class LydiaConfigForm(forms.Form):
    lydia_min_price = forms.DecimalField(label='Montant minimal de rechargement',
                                        decimal_places=2, max_digits=9,
                                        validators=[
                                          MinValueValidator(0, 'Le montant doit être positif')],
                                        required=False)
    lydia_max_price = forms.DecimalField(label='Montant maximal de rechargement',
                                        decimal_places=2, max_digits=9,
                                        validators=[
                                          MinValueValidator(0, 'Le montant doit être positif')],
                                        required=False)
