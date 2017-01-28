from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from shops.models import Shop, ProductBase


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
    product_bases = models.ManyToManyField('shops.ProductBase')


class Module(models.Model):
    class Meta:
        abstract = True

    state = models.BooleanField('Activé', default = False)


class ShopModule(Module):
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


class SelfSaleModule(ShopModule):
    """
    Define Permissions for SelfSaleModule.
    """
    class Meta:
        permissions = (
            ('use_selfsalemodule',
             'Consommer aux magasins par libre service'),
        )


class OperatorSaleModule(ShopModule):
    """
    Define Permissions for OperatorSaleModule.
    """
    class Meta:
        permissions = (
            ('use_operatorsalemodule',
             'Consommer aux magasins avec un opérateur'),
        )
