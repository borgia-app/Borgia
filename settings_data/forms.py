from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class PriceConfigForm(forms.Form):
    margin_profit = forms.DecimalField(label='Marge appliquée aux prix en mode automatique',
                                        decimal_places=2, max_digits=9,
                                        validators=[
                                          MinValueValidator(0, 'Le montant doit être positif')])


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
    def clean(self):
        """
        If min and max:
            max >= min
        """
        cleaned_data = super(LydiaConfigForm, self).clean()
        lydia_min_price = cleaned_data.get("lydia_min_price", None)
        lydia_max_price = cleaned_data.get("lydia_max_price", None)
        if lydia_min_price is not None and lydia_max_price is not None:
            if lydia_max_price < lydia_min_price:
                raise ValidationError("Le montant maximal doit être supérieur ou égal au montant minimal")


class BalanceConfigForm(forms.Form):
    balance_threshold_mail_alert = forms.DecimalField(label='Valeur seuil',
                                        decimal_places=2, max_digits=9,
                                        required=False)
    balance_frequency_mail_alert = forms.IntegerField(label='Fréquence des emails d\'alerte',
                                        validators=[
                                          MinValueValidator(1, 'La fréquence doit être d\'au moins 1 jour')],
                                        required=False)
