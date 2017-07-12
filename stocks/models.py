from decimal import Decimal

from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator


class StockEntry(models.Model):
    datetime = models.DateTimeField('Date', default=now)
    operator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    products = models.ManyToManyField('shops.Product', through='StockEntryProduct')
    shop = models.ForeignKey('shops.Shop',on_delete=models.CASCADE)

    def total(self):
        total = sum(sep.price for sep in self.stockentryproduct_set.all())
        return total

    def string_products(self):
        string = ''
        for spe in self.stockentryproduct_set.all():
            string += spe.__str__() + ', '
        string = string[0: len(string)-2]
        return string

    class Meta:
        permissions = (
            ('list_stockentry', 'Lister les entrées de stock'),
            ('retrieve_stockentry', 'Afficher les entrées de stock'),
        )


class StockEntryProduct(models.Model):
    """
    quantity -> in CL/G (even if L/KG is possible in the form)
    price -> price for the whole quantity (even if price for L/KG is possible in the form)
    """
    stockentry = models.ForeignKey('StockEntry', on_delete=models.CASCADE)
    product = models.ForeignKey('shops.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField('Prix', default=0, decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(Decimal(0))])

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
    datetime = models.DateTimeField('Date', default=now)
    operator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    products = models.ManyToManyField('shops.Product', through='InventoryProduct')
    shop = models.ForeignKey('shops.Shop',on_delete=models.CASCADE)

    class Meta:
        permissions = (
            ('list_inventory', 'Lister les inventaires de stock'),
            ('retrieve_inventory', 'Afficher les inventaires de stock'),
        )

    def update_correcting_factors(self):
        for inventoryproduct in self.inventoryproduct_set.all():
            inventoryproduct.product.update_correcting_factor(inventoryproduct.quantity)


class InventoryProduct(models.Model):
    """
    quantity -> in CL/G (even if L/KG is possible in the form)
    """
    inventory = models.ForeignKey('Inventory', on_delete=models.CASCADE)
    product = models.ForeignKey('shops.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def get_quantity_display(self):
        return self.product.get_quantity_display(self.quantity)
