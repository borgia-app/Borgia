import decimal

from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import MinValueValidator
from django.db import models

from shops.models import Product, Shop


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
    products = models.ManyToManyField(Product, through='CategoryProduct')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        """
        Remove default permissions for Category
        """
        default_permissions = ()


class CategoryProduct(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        """
        Remove default permissions for CategoryProduct
        """
        default_permissions = ()

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
                    return decimal.Decimal(self.quantity * self.product.get_price() / 100)
                if self.product.unit == 'G':
                    return decimal.Decimal(self.quantity * self.product.get_price() / 1000)
            else:
                return decimal.Decimal(self.product.get_price())
        except (ZeroDivisionError, decimal.DivisionUndefined, decimal.DivisionByZero):
            return decimal.Decimal(0)


class Module(models.Model):
    state = models.BooleanField('Activé', default=False)

    class Meta:
        abstract = True


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
    shop = models.ForeignKey(
        Shop,
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

    class Meta:
        abstract = True

    def get_module_class(self):
        """
        Return the module type.
        Must be overridden.
        """
        raise ImproperlyConfigured(
            '{0} is using get_module_class() of ShopModule model.'
            'You must override {0}.get_module_class().'.format(self.__class__.__name__)
        )

class SelfSaleModule(ShopModule):
    """
    Define Permissions for SelfSaleModule.
    """
    class Meta:
        default_permissions = ()
        permissions = (
            ('use_selfsalemodule', 'Can use the self sale module'),
            ('change_config_selfsalemodule', 'Can change the config for self sale module'),
            ('view_config_selfsalemodule', 'Can view the config for self sale module')
        )

    def __str__(self):
        return 'Module de vente en libre service du magasin ' + self.shop.__str__()

    def get_module_class(self):
        return 'self_sales'


class OperatorSaleModule(ShopModule):
    """
    Define Permissions for OperatorSaleModule.
    """
    class Meta:
        default_permissions = ()
        permissions = (
            ('use_operatorsalemodule', 'Can use the operator sale module'),
            ('change_config_operatorsalemodule', 'Can change the config for operator sale module'),
            ('view_config_operatorsalemodule', 'Can view the config for operator sale module')
        )

    def __str__(self):
        return 'Module de vente par opérateur du magasin ' + self.shop.__str__()

    def get_module_class(self):
        return 'operator_sales'
