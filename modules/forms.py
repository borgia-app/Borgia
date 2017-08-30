from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator

from shops.models import Product
from modules.models import CategoryProduct
from users.models import User
from django.db.utils import OperationalError, ProgrammingError


class SelfSaleShopModule(forms.Form):
    def __init__(self, *args, **kwargs):
        self.module = kwargs.pop('module')
        self.client = kwargs.pop('client')
        super(SelfSaleShopModule, self).__init__(*args, **kwargs)

        try:
            self.fields['client'] = self.get_client_field()
        except AttributeError:
            pass

        for category in self.module.categories.all():
            for category_product in category.categoryproduct_set.all():
                if category_product.get_price() > 0:
                    self.fields[str(category_product.pk)
                                 + '-' + str(category.pk)
                                 ] = forms.IntegerField(
                        label=category_product.__str__(),
                        widget=forms.NumberInput(
                            attrs={'data_category_pk': category.pk,
                                   'data_price': category_product.get_price(),
                                   'class': 'form-control',
                                   'pk': (
                                       str(category_product.product.pk)
                                       + '-'
                                       + str(category.pk)),
									'min': 0}),
                        initial=0,
                        required=False,
                        validators=[MinValueValidator(0, """La commande doit être
                                                      positive ou nulle""")]
                        )


    def clean(self):
        cleaned_data = super(SelfSaleShopModule, self).clean()
        if self.client is None:
            try:
                self.client = User.objects.get(
                    pk=cleaned_data['client'].split('/')[0])
            except ObjectDoesNotExist:
                raise forms.ValidationError('Utilisateur inconnu')
            except KeyError:
                raise forms.ValidationError('Utilisateur non sélectionné')
        total_price = 0
        for field in cleaned_data:
            if field != 'client':
                invoice = cleaned_data[field]
                if isinstance(invoice, int) and invoice > 0 :
                    try:
                        category_product_pk = field.split('-')[0]
                        total_price += (CategoryProduct.objects.get(pk=category_product_pk).get_price() * invoice)
                    except ObjectDoesNotExist:
                        pass
        if total_price > self.client.balance:
            raise forms.ValidationError('Crédit insuffisant !')
        if self.module.limit_purchase:
            if total_price > self.module.limit_purchase:
                raise forms.ValidationError('Le montant est supérieur à la limite.')
        if total_price <= 0:
            raise forms.ValidationError('La commande doit être positive.')


class OperatorSaleShopModule(SelfSaleShopModule):
    def get_client_field(self):
        try:
            return forms.ChoiceField(
                label='Client',
                choices=([(None, 'Selectionner un client')] + [(str(u.pk)+'/'+str(u.balance), u.choice_string())
                         for u in User.objects.all().exclude(groups__pk=1)]),
                widget=forms.Select(
                    attrs={'class': 'form-control selectpicker',
                           'data-live-search': 'True'})
            )
        except OperationalError:
            pass
        except ProgrammingError:
            pass

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
            queryset=Product.objects.filter(shop=shop),
            widget=forms.SelectMultiple(attrs={'class': 'selectpicker',
                                               'data-live-search': 'True'}),
            required=False)


class ModuleCategoryCreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super(ModuleCategoryCreateForm, self).__init__(*args, **kwargs)
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
                    'placeholder': 'En vente',
                    'min':1}
        )
    )

    def clean(self):
        cleaned_data = super(ModuleCategoryCreateForm, self).clean()
        # Validation direct in html



class ModuleCategoryCreateNameForm(forms.Form):
    name = forms.CharField(
        label='Nom',
        max_length=254
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
