from decimal import Decimal

from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator


class StockEntry(models.Model):
    datetime = models.DateTimeField('Date', default=now)
    operator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    products = models.ManyToManyField('shops.Product', through='StockEntryProduct')


class StockEntryProduct(models.Model):
    """
    price -> price for the whole quantity
    """
    stockentry = models.ForeignKey('StockEntry', on_delete=models.CASCADE)
    product = models.ForeignKey('shops.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField('Prix', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])


class Inventory(models.Model):
    pass


class InventoryProduct(models.Model):
    pass
