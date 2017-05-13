from django import forms
from django.forms.models import ModelChoiceField

from shops.models import (Shop, Container, ProductBase, ProductUnit, SingleProduct)
from modules.models import ContainerCase
from borgia.validators import autocomplete_username_validator


class ProductCreateForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ProductCreateForm, self).__init__(**kwargs)
        if shop:
            self.fields['product_base'] = forms.ModelChoiceField(
                label='Base produit', queryset=ProductBase.objects.filter(
                    shop=shop, is_active=True).exclude(pk=1).order_by('name'),
                widget=forms.Select(
                    attrs={'class': 'selectpicker form-control',
                           'data-live-search': 'True'}))
        else:
            self.fields['product_base'] = forms.ModelChoiceField(
                label='Base produit', queryset=ProductBase.objects.filter(
                    is_active=True).exclude(pk=1).order_by('name'),
                widget=forms.Select(
                    attrs={'class': 'selectpicker form-control',
                           'data-live-search': 'True'}))
        self.fields['quantity'] = forms.IntegerField(
            label="""Quantité à ajouter (de Fût, en KG, ou de bouteille). Attention, dans le cas de viande ou de fromage, la quantité correspond au poids (en gr) du produit acheté, exemple: un morceau de Brie de 1500 gr.""",
            min_value=0, max_value=5000)
        self.fields['price'] = forms.DecimalField(
            label="""Prix d'achat TTC (par Fût, KG, bouteille). Attention, dans le cas de viande ou de fromage, le prix de vente est le prix du morceau total dont le poids est entré plus haut, exemple: 120€ pour un morceau de Brie de 1500gr.""",
            decimal_places=2, max_digits=9, min_value=0)
        self.fields['purchase_date'] = forms.DateField(
            label='Date d\'achat',
            widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['expiry_date'] = forms.DateField(
            label='Date d\'expiration', required=False,
            widget=forms.DateInput(attrs={'class': 'datepicker'}))
        self.fields['place'] = forms.CharField(max_length=255,
                                               label='Lieu de stockage')


class ProductBaseCreateForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ProductBaseCreateForm, self).__init__(**kwargs)

        if shop:
            self.fields['type'] = forms.ChoiceField(
                label='Type de produit',
                choices=(('container', 'Conteneur'),
                         ('single_product', 'Produit unitaire'))
            )
            self.fields['product_unit'] = forms.ModelChoiceField(
                label='Unité de produit',
                queryset=ProductUnit.objects.filter(
                    shop=shop, is_active=True).exclude(pk=1),
                required=False,
                widget=forms.Select(
                    attrs={'class': 'selectpicker form-control',
                           'data-live-search': 'true'})
            )
        else:
            self.fields['shop'] = forms.ModelChoiceField(
                label='Magasin',
                queryset=Shop.objects.all().exclude(pk=1)
            )
            self.fields['type'] = forms.ChoiceField(
                label='Type de produit',
                choices=(('container', 'Conteneur'),
                         ('single_product', 'Produit unitaire'))
            )
            self.fields['product_unit'] = forms.ModelChoiceField(
                label='Unité de produit',
                queryset=ProductUnit.objects.filter(
                    is_active=True).exclude(pk=1),
                required=False,
                widget=forms.Select(
                    attrs={'class': 'selectpicker form-control',
                           'data-live-search': 'true'})
            )
        self.fields['quantity'] = forms.IntegerField(
            label='Quantité de produit unitaire (g, cl ...). Attention, dans le cas de viande ou de fromage, la quantité doit toujours être 1000.',
            min_value=0,
            required=False
        )
        self.fields['name'] = forms.CharField(
            label='Nom',
            max_length=254,
            required=False
        )
        self.fields['brand'] = forms.CharField(max_length=255,
                                               label='Marque')


    def clean(self):
        cleaned_data = super(ProductBaseCreateForm, self).clean()
        type = cleaned_data.get('type')
        product_unit = cleaned_data.get('product_unit')
        quantity = cleaned_data.get('quantity')
        name = cleaned_data.get('name')
        if type == 'container':
            if product_unit is None:
                raise forms.ValidationError(
                    'Une unité de produit est exigée pour un conteneur'
                )
            if quantity is None:
                raise forms.ValidationError(
                    'Une quantité d\'unité de produit est exigée pour un conteneur'
                )
        else:
            if name is None or name == '':
                raise forms.ValidationError(
                    """Un nom est obligatoire pour un produit unitaire"""
                )


class ProductUnitCreateForm(forms.Form):
    def __init__(self, **kwargs):
        shop = kwargs.pop('shop')
        super(ProductUnitCreateForm, self).__init__(**kwargs)
        self.fields['name'] = forms.CharField(max_length=255,
                                              label='Nom')
        self.fields['unit'] = forms.ChoiceField(
            label='Unité de calcul',
            choices=(('CL', 'cl'), ('G', 'g')))
        self.fields['type'] = forms.ChoiceField(
            label='Catégorie de produit',
            choices=(('keg', 'fût'), ('liquor', 'alcool fort'),
                     ('syrup', 'sirop'), ('soft', 'soft'),
                     ('food', 'alimentaire'), ('meat', 'viande'),
                     ('cheese', 'fromage'), ('side', 'accompagnement')))
        if shop is None:
            self.fields['shop'] = forms.ModelChoiceField(
                label='Magasin',
                queryset=Shop.objects.all().exclude(pk=1)
            )


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = ProductBase
        fields = ['name', 'description', 'brand', 'type', 'quantity',
                  'product_unit']


class ProductUpdatePriceForm(forms.Form):
    is_manual = forms.BooleanField(
        label='Gestion manuelle du prix', required=False)
    manual_price = forms.DecimalField(label='Prix manuel',
                                      decimal_places=2,
                                      max_digits=9, min_value=0,
                                      required=False)


class ProductStockRegularisationForm(forms.Form):
    def __init__(self, **kwargs):
        product_base = kwargs.pop('product_base')
        self.product_base = product_base
        super(ProductStockRegularisationForm, self).__init__(**kwargs)
        self.fields['number'] = forms.IntegerField(
            label='Nombre de régularisation(s)',
            min_value=1
            )
        self.fields['type'] = forms.ChoiceField(
            label='Type de régularisation',
            choices=(('out', 'Sortie du stock'),
                     ('in', 'Entrée au stock')))
        self.fields['occasion'] = forms.ChoiceField(
            label="""A l'occasion de""",
            choices=(('sell', "Vente externe à l'association"),
                     ('inventory', 'Inventaire du stock')),
            required=False)
        self.fields['sell_price'] = forms.DecimalField(
                    label="""Prix de vente en €""",
                    decimal_places=2, max_digits=9, min_value=0,
                    required=False)
        self.fields['justification'] = forms.CharField(max_length=255,
                                                label='justification',
                                                required=False)

    def clean(self):
        cleaned_data = super(ProductStockRegularisationForm, self).clean()
        type = cleaned_data.get('type')
        number = cleaned_data.get('number')
        quantity = cleaned_data.get('quantity')
        occasion = cleaned_data.get('occasion')
        sell_price = cleaned_data.get('sell_price')
        justification = cleaned_data.get('justification')
        if type == 'out':
            if number > self.product_base.quantity_products_stock():
                raise forms.ValidationError(
                    """Vous essayez de sortir plus de produits que le nombre en stock actuellement."""
                )
            if not sell_price and occasion == 'sell':
                raise forms.ValidationError(
                    """Le prix de vente est obligatoire."""
                )
            if not justification and occasion == 'sell':
                raise forms.ValidationError(
                    """La justification est obligatoire."""
                )
        else:
            if self.product_base.get_moded_price() == 0:
                if self.product_base.type == 'container':
                    if Container.objects.filter(product_base=self.product_base).count() == 0:
                        raise forms.ValidationError(
                            """Il n'y a jamais eu de produits en vente de ce type, Borgia ne peut pas déterminer le prix de vente usuel."""
                        )
                else:
                    if SingleProduct.objects.filter(product_base=self.product_base).count() == 0:
                        raise forms.ValidationError(
                            """Il n'y a jamais eu de produits en vente de ce type, Borgia ne peut pas déterminer le prix de vente usuel."""
                        )


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
        self.fields['type'] = forms.ChoiceField(
            label='Type de produit',
            choices=(('container', 'Conteneur'),
                     ('single_product', 'Produit unitaire')),
            required=False)


class ShopContainerCaseForm(forms.Form):
    name = forms.CharField(
        label='Nom',
        max_length=254
    )
    pk = forms.IntegerField(
        label='Pk',
        widget=forms.HiddenInput(),
        required=False
    )
    percentage = forms.FloatField(
        label='percentage',
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop')
        super(ShopContainerCaseForm, self).__init__(*args, **kwargs)
        q = ProductBase.objects.filter(shop=shop, type='container')
        q_ids = [o.id for o in q if (o.quantity_products_stock() != 0)]
        q = q.filter(id__in=q_ids)
        self.fields['base_container'] = ModelChoiceFieldContainerWithQuantity(
            label='Conteneur',
            queryset=q,
            widget=forms.Select(attrs={'class': 'selectpicker',
                                       'data-live-search': 'True'}),
            required=False)
        self.fields['is_sold'] = forms.BooleanField(
            label='Le fût changé était vide ?',
            initial=False,
            required=False)


class ModelChoiceFieldContainerWithQuantity(ModelChoiceField):
    """
    """

    def label_from_instance(self, obj):
        # Count stock
        list_container = Container.objects.filter(
            product_base=obj, is_sold=False)
        # Remove container at container_cases
        in_container_cases = 0
        for container_case in ContainerCase.objects.all():
            if container_case.product:
                if (container_case.product.product_base == obj):
                    in_container_cases += 1
        # Remove quantity at container_cases
        quantity_in_stock = list_container.count() - in_container_cases
        return obj.__str__() + ' (' + str(quantity_in_stock) + ')'
