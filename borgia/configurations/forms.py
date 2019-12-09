from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class ConfigurationCenterForm(forms.Form):
    center_name = forms.CharField(label='Nom du centre Borgia', max_length=255)


class ConfigurationProfitForm(forms.Form):
    margin_profit = forms.DecimalField(label='Marge appliquée aux prix en mode automatique (%)',
                                       decimal_places=2, max_digits=9,
                                       validators=[
                                           MinValueValidator(0, 'Le montant doit être positif')])


class ConfigurationLydiaForm(forms.Form):
    enable_self_lydia = forms.BooleanField(label='Activer le rechargement par Lydia',
                                           required=False)
    min_price_lydia = forms.DecimalField(label='Montant minimal de rechargement (€)',
                                         decimal_places=2, max_digits=9,
                                         validators=[
                                             MinValueValidator(0.01, 'Le montant doit être strict. positif')]
                                         )
    max_price_lydia = forms.DecimalField(label='Montant maximal de rechargement (€)',
                                         decimal_places=2, max_digits=9,
                                         validators=[
                                             MinValueValidator(0.01, 'Le montant doit être strict. positif')],
                                         required=False)
    enable_fee_lydia = forms.BooleanField(
        label='Prendre en compte la commission Lydia',
        required=False)
    base_fee_lydia = forms.DecimalField(label='Montant de la commission : Base HT (€)',
                                        decimal_places=2, max_digits=9,
                                        validators=[
                                            MinValueValidator(0, 'Le montant doit être positif')],
                                        required=False)
    ratio_fee_lydia = forms.FloatField(label='Montant de la commission : Pourcentage (%)',
                                       validators=[
                                             MinValueValidator(0, 'Le montant doit être positif')],
                                       required=False)
    tax_fee_lydia = forms.FloatField(label='Montant de la commission : Taxe',
                                       validators=[
                                             MinValueValidator(0, 'Le montant doit être positif')],
                                       required=False)
    api_token_lydia = forms.CharField(label='Clé API (privée)', max_length=255)
    vendor_token_lydia = forms.CharField(
        label='Clé vendeur (publique)', max_length=255)

    def clean(self):
        """
        If min and max:
            max >= min
        """
        cleaned_data = super().clean()
        min_price_lydia = cleaned_data.get("min_price_lydia")
        max_price_lydia = cleaned_data.get("max_price_lydia", None)
        if max_price_lydia is not None:
            if max_price_lydia < min_price_lydia:
                raise ValidationError(
                    "Le montant maximal doit être supérieur ou égal au montant minimal")


        enable_self_lydia = cleaned_data.get("enable_self_lydia", None)
        enable_fee_lydia = cleaned_data.get("enable_fee_lydia", None)
        if enable_fee_lydia is not None:
            if enable_fee_lydia and (enable_self_lydia is None or not enable_self_lydia):
                raise ValidationError(
                   "Pour prendre en compte la commission Lydia, le rechargement"
                  +" à distance via Lydia doit être activé")

class ConfigurationBalanceForm(forms.Form):
    balance_threshold_purchase = forms.DecimalField(label='Valeur seuil (€) pour pouvoir acheter',
                                                    decimal_places=2, max_digits=9)

    # balance_threshold_mail_alert = forms.DecimalField(label='Valeur seuil (€) de l\'alerte par email',
    #                                     decimal_places=2, max_digits=9,
    #                                     required=False)
    # balance_frequency_mail_alert = forms.IntegerField(label='Fréquence de l\'alerte par email',
    #                                     validators=[
    #                                       MinValueValidator(1, 'La fréquence doit être d\'au moins 1 jour')],
    #                                     required=False)
