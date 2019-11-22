from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator

from modules.models import CategoryProduct
from shops.models import Product
from users.models import User


class ShopModuleSaleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.module_class = kwargs.pop('module_class')
        self.module = kwargs.pop('module')
        self.client = kwargs.pop('client')
        self.balance_threshold_purchase = kwargs.pop(
            'balance_threshold_purchase')
        super().__init__(*args, **kwargs)

        if self.module_class == 'operator_sales':
            self.fields['client'] = self.get_client_field()

        for category in self.module.categories.all():
            for category_product in category.categoryproduct_set.all():
                if (category_product.get_price() > 0 and
                        not category_product.product.is_removed and
                        category_product.product.is_active):
                    self.fields[str(category_product.pk)
                                + '-' + str(category.pk)
                                ] = forms.IntegerField(
                                    label=category_product.__str__(),
                                    widget=forms.NumberInput(
                                        attrs={'data_category_pk': category.pk,
                                               'data_price': category_product.get_price(),
                                               'class': 'form-control buyable_product',
                                               'min': 0}),
                                    initial=0,
                                    required=False,
                                    validators=[MinValueValidator(0, """La commande doit être
                                                                positive ou nulle""")])

    def clean(self):
        super().clean()
        if self.client is None:
            try:
                self.client = User.objects.get(
                    username=self.cleaned_data['client'])
            except ObjectDoesNotExist:
                raise forms.ValidationError("L'utilisateur n'existe pas")
            except KeyError:
                raise forms.ValidationError('Utilisateur non sélectionné')
            if not self.client.is_active:
                raise forms.ValidationError("L'utilisateur a été desactivé")
        total_price = 0
        for field in self.cleaned_data:
            if field != 'client':
                invoice = self.cleaned_data[field]
                if isinstance(invoice, int) and invoice > 0:
                    try:
                        category_product_pk = field.split('-')[0]
                        total_price += (CategoryProduct.objects.get(
                            pk=category_product_pk).get_price() * invoice)
                    except ObjectDoesNotExist:
                        pass
        if (self.client.balance - total_price) < self.balance_threshold_purchase.get_value():
            raise forms.ValidationError('Crédit insuffisant !')
        if self.module.limit_purchase:
            if total_price > self.module.limit_purchase:
                raise forms.ValidationError(
                    'Le montant est supérieur à la limite.')
        if total_price <= 0:
            raise forms.ValidationError('La commande doit être positive.')

        self.cleaned_data['client'] = self.client
        return self.cleaned_data

    def get_client_field(self):
        return forms.CharField(
            label="Client",
            max_length=255,
            required=True,
            widget=forms.TextInput(attrs={'class': 'form-control autocomplete_username',
                                          'autocomplete': 'off',
                                          'autofocus': 'true',
                                          'placeholder': "Nom d'utilisateur"}))

class ModuleCategoryCreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super().__init__(*args, **kwargs)
        self.fields['product'] = forms.ChoiceField(
            label='Produit',
            choices=([(None, 'Sélectionner un produit')] + [
                (str(product.pk)+'/'+str(product.get_unit_display()),
                 product.__str__())
                for product in Product.objects.filter(shop=shop, is_removed=False, is_active=True)
            ] + [
                (str(product.pk)+'/'+str(product.get_unit_display()),
                 product.__str__() + ' DESACTIVE')
                for product in Product.objects.filter(shop=shop, is_removed=False, is_active=False)
            ]),
            widget=forms.Select(
                attrs={'class': 'form-control selectpicker',
                       'data-live-search': 'True'})
        )
    quantity = forms.IntegerField(
        label='En vente',
        required=False,
        widget=forms.NumberInput(
            attrs={'class': 'form-control centered_input quantity',
                   'placeholder': 'En vente',
                   'min': 1}
        )
    )

    # TODO : Validation


class ModuleCategoryCreateNameForm(forms.Form):
    name = forms.CharField(
        label='Nom',
        max_length=254
    )
    order = forms.IntegerField(
        label='Ordre',
        min_value=0,
        validators=[MinValueValidator(0,'Cette valeur doit être positive')],
        required=True,
        help_text="L'ordre des catégories commence à partir de 0 !"
    )


class ShopModuleConfigForm(forms.Form):
    state = forms.BooleanField(
        label='Activé',
        required=False
    )
    logout_post_purchase = forms.BooleanField(
        label='Déconnexion après une vente',
        required=False
    )
    limit_purchase = forms.DecimalField(label='Montant limite de commande',
                                        decimal_places=2, max_digits=9,
                                        validators=[
                                            MinValueValidator(0, 'Le montant doit être positif')],
                                        required=False)
    infinite_delay_post_purchase = forms.BooleanField(
        label="Durée d'affichage du résumé de commande infini",
        required=False
    )
    delay_post_purchase = forms.IntegerField(label="Durée (en secondes)",
                                             validators=[
                                                 MinValueValidator(0, 'La durée doit être positive')],
                                             required=False)
