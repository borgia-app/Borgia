import decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now

from shops.models import Product, Shop
from users.models import User


class Sale(models.Model):
    """
    Define a Sale between two users.

    The transaction is managed by an operator (which can the the sender
    directly if the sell is direct). Most of sale are between an User and the
    association (represented by the special User with username 'AE ENSAM').

    :param datetime: date of sell, mandatory.
    :param sender: sender of the sale, mandatory.
    :param recipient: recipient of the sale, mandatory.
    :param operator: operator of the sale, mandatory.

    NEW IMPLMENTATION
    :param content_type:
    :param module_id:
    :param module:
    :param shop:
    :param products:


    :type datetime: date string, default now
    :type sender: User object
    :type recipient: User object
    :type operator: User object

    NEW IMPLMENTATION
    :type content_type:
    :type module_id:
    :type module:
    :type shop: Shop object
    :type products: Product object

    :note:: Initial Django Permission (add, change, delete, view) are added.
    """
    datetime = models.DateTimeField('Date', default=now)
    sender = models.ForeignKey(User, related_name='sender_sale',
                               on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient_sale',
                                  on_delete=models.CASCADE)
    operator = models.ForeignKey(User, related_name='operator_sale',
                                 on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    module_id = models.PositiveIntegerField()
    module = GenericForeignKey('content_type', 'module_id')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='SaleProduct')

    def __str__(self):
        """
        Return the display name of the Sale.

        :returns: pk of sale
        :rtype: string
        """
        return 'Achat ' + self.shop.__str__() + ', ' + self.string_products()

    def pay(self):
        self.sender.debit(self.amount())

    def string_products(self):
        """
        Return a formated string concerning all products in this Sale.

        :returns: each __str__ of products, separated by a comma.
        :rtype: string

        :note:: Why do Events are excluded ?
        """
        string = ''
        for sp in self.saleproduct_set.all():
            string += sp.__str__() + ', '
        string = string[0: len(string)-2]
        return string

    def from_shop(self):
        try:
            return self.module.shop
        except ObjectDoesNotExist:
            return None
        except IndexError:
            return None

    def amount(self):
        amount = 0
        for sale_product in self.saleproduct_set.all():
            amount += sale_product.price
        return amount


class SaleProduct(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField('Prix', default=0, decimal_places=2,
                                max_digits=9,
                                validators=[MinValueValidator(decimal.Decimal(0))])

    class Meta:
        """
        Remove default permissions for StockEntryProduct
        """
        default_permissions = ()

    def __str__(self):
        if self.product.unit:
            return self.product.__str__() + ' x ' + str(self.quantity) + self.product.get_unit_display()
        else:
            if self.quantity > 1:
                return self.product.__str__() + ' x ' + str(self.quantity)
            else:
                return self.product.__str__()
