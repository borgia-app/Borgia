from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now

from shops.models import Product, Shop
from users.models import User


class StockEntry(models.Model):
    """
    Used when buying products for a shop.

    :note:: Initial Django Permission (add, change, delete, view) are added.
    """
    datetime = models.DateTimeField('Date', default=now)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='StockEntryProduct')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def total(self):
        total = sum(sep.price for sep in self.stockentryproduct_set.all())
        return total

    def string_products(self):
        string = ''
        for sep in self.stockentryproduct_set.all():
            string += sep.__str__() + ', '
        string = string[0: len(string)-2]
        return string


class StockEntryProduct(models.Model):
    """
    quantity -> in CL/G (even if L/KG is possible in the form)
    price -> price for the whole quantity (even if price for L/KG is possible in the form)
    """
    stockentry = models.ForeignKey(StockEntry, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField('Prix', default=0, decimal_places=2,
                                max_digits=9,
                                validators=[MinValueValidator(Decimal(0))])

    class Meta:
        """
        Remove default permissions for StockEntryProduct
        """
        default_permissions = ()

    def __str__(self):
        if self.product.unit:
            return self.product.__str__() + ' x ' + str(self.quantity) + self.product.get_unit_display()
        else:
            return self.product.__str__() + ' x ' + str(self.quantity)

    def unit_price(self):
        if self.product.unit:
            if self.product.unit == 'G':
                return Decimal(1000 * self.price / self.quantity)
            if self.product.unit == 'CL':
                return Decimal(100 * self.price / self.quantity)
        else:
            return Decimal(self.price / self.quantity)


class Inventory(models.Model):
    """
    Used to do an inventory of a shop stock.

    :note:: Initial Django Permission (add, change, delete, view) are added.
    """

    datetime = models.DateTimeField('Date', default=now)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='InventoryProduct')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def update_correcting_factors(self):
        for inventoryproduct in self.inventoryproduct_set.all():
            inventoryproduct.product.update_correcting_factor(
                inventoryproduct.quantity)


class InventoryProduct(models.Model):
    """
    quantity -> in CL/G (even if L/KG is possible in the form)
    """
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        """
        Remove default permissions for InventoryProduct
        """
        default_permissions = ()

    def get_quantity_display(self):
        return self.product.get_quantity_display(self.quantity)
