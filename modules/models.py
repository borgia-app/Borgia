import decimal

from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    """
    :note:: Using generic foreign keys, filter api doesn't work. It doesn't
    work with ModelForm too.
    :note:: Should we use several category types here ? In order to use filter
    api and ModelForm ? For instance CategorySelfSaleModule, etc ...
    However one can filter with the module_id field.
    For instance to filter all categories related to a module:
    Category.objects.filter(module_id = mymodule.id)
    """
    name = models.CharField('Nom', max_length=254)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    module_id = models.PositiveIntegerField()
    module = GenericForeignKey('content_type', 'module_id')
    products = models.ManyToManyField('shops.Product', through='CategoryProduct')


class CategoryProduct(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    product = models.ForeignKey('shops.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        if self.product.unit:
            return self.product.name + ' / ' + str(self.quantity) + self.product.get_unit_display()
        return self.product.name

    def get_price(self):
        """
        Return the price for the quantity.
        """
        try:
            if self.product.unit:
                # - price for a L, quantity in cl
                # - price for a kg, quantity in kg
                if self.product.unit == 'CL':
                    return decimal.Decimal(self.quantity * self.product.get_price() /  100)
                if self.product.unit == 'G':
                    return decimal.Decimal(self.quantity * self.product.get_price() / 1000)
            else:
                return decimal.Decimal(self.product.get_price())
        except (ZeroDivisionError, decimal.DivisionUndefined, decimal.DivisionByZero):
            return decimal.Decimal(0)


class Module(models.Model):
    class Meta:
        abstract = True

    state = models.BooleanField('Activé', default=False)


class ShopModule(Module):
    """

    :param delay_post_purchase: Delay the resume of the sale will be displayed.
    If the delay is null, the resume is not display. In seconds, positiv.
    :param limit_purchase: Limit of amount for a sale through this module,
    If null, there is no limit. Positiv.
    :param logout_post_purchase: If True, the user will be logout after the
    sale, mandatory.
    :type delay_post_purchase: Integer, in seconds.
    :type limit_purchase: Float (Decimal).
    :type logout_post_purchase: Boolean.
    """
    class Meta:
        abstract = True

    shop = models.ForeignKey(
        'shops.Shop',
        related_name='%(app_label)s_%(class)s_shop',
        on_delete=models.CASCADE)
    categories = GenericRelation(
        Category,
        content_type_field='content_type',
        object_id_field='module_id')
    delay_post_purchase = models.IntegerField("Durée d'affichage du résumé de commande",
                                              validators=[
                                                MinValueValidator(decimal.Decimal(0))],
                                              blank=True, null=True)
    limit_purchase = models.DecimalField('Montant limite de commande',
                                         decimal_places=2, max_digits=9,
                                         validators=[
                                           MinValueValidator(decimal.Decimal(0))],
                                         blank=True, null=True)
    logout_post_purchase = models.BooleanField('Deconnexion après une vente',
                                               default=False)


class SelfSaleModule(ShopModule):
    """
    Define Permissions for SelfSaleModule.
    """
    class Meta:
        permissions = (
            ('use_selfsalemodule',
             'Consommer aux magasins par libre service'),
        )

    def __str__(self):
        return 'module de vente en libre service du magasin ' + self.shop.__str__()


class OperatorSaleModule(ShopModule):
    """
    Define Permissions for OperatorSaleModule.
    """
    class Meta:
        permissions = (
            ('use_operatorsalemodule',
             'Consommer aux magasins avec un opérateur'),
        )

    def __str__(self):
        return 'module de vente par opérateur du magasin ' + self.shop.__str__()
