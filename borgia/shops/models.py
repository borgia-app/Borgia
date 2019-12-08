import decimal

from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from configurations.utils import configuration_get


class Shop(models.Model):
    """
    Define a Shop object.

    A shop represent a virtual place (can be physical though) where products
    are sold. Each shop can have several module which can be enable or not by
    modifying Shop object attributes.

    :param name: Display name, mandatory.
    :param description: Description, mandatory.
    :param color: Color, mandatory.
    :type name: string
    :type description: string
    :type color: string

    :note:: Initial Django Permission (add, change, delete, view) are added.
    """
    name = models.CharField('Code', max_length=255,
                            validators=[RegexValidator(
                                regex='^[a-z]+$',
                                message="""Ne doit contenir que des lettres
                                minuscules, sans espace ni caractère
                                spécial.""")])
    description = models.TextField('Description')
    color = models.CharField('Couleur', max_length=255,
                             validators=[RegexValidator(
                                 regex='^#[A-Za-z0-9]{6}',
                                 message='Doit être dans le format #F4FA58')])

    def __str__(self):
        """
        Return the display name.

        :returns: name attribute
        :rtype: string
        """
        return self.name.capitalize()

    def get_managers(self):
        try:
            chiefs_group = Group.objects.get(name='chiefs-' + self.name)
            associates_group = Group.objects.get(
                name='associates-' + self.name)
        except ObjectDoesNotExist:
            raise ImproperlyConfigured(
                '{0} is missing the related managers groups. You should verify the name of '
                '{0} and/or the managers groups related'.format(
                    self.__class__.__name__)
            )

        managers = chiefs_group.user_set.union(associates_group.user_set.all())
        return managers


class Product(models.Model):
    """
    Define a Product object.

    :param name: Display name, mandatory.
    :param is_manual: is the price set manually.
    :param manual_price: price if set manually.
    :param shop: Related shop.
    :param is_active: is the product used.
    :param is_removed: is the product removed.
    :param unit: unit of the product.
    :param correcting_factor: for automatic price.
    :type name: string
    :type is_manual: bool
    :type manual_price: decimal
    :type shop:
    :type is_active: bool
    :type is_removed: bool
    :type unit: string
    :type correcting_factor: decimal
    """
    UNIT_CHOICES = (('CL', 'cl'), ('G', 'g'))

    name = models.CharField('Nom', max_length=255)
    unit = models.CharField('Unité', max_length=255,
                            choices=UNIT_CHOICES, blank=True, null=True)
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE)
    is_manual = models.BooleanField('Gestion manuelle du prix', default=False)
    manual_price = models.DecimalField('Prix manuel', default=0,
                                       decimal_places=2, max_digits=9,
                                       validators=[
                                           MinValueValidator(decimal.Decimal(0))])
    correcting_factor = models.DecimalField('Facteur correcteur de ventes', default=1,
                                            decimal_places=4, max_digits=9,
                                            validators=[
                                                MinValueValidator(decimal.Decimal(0))])
    is_active = models.BooleanField('Actif', default=True)
    is_removed = models.BooleanField('Retiré', default=False)

    class Meta:
        """
        Define Permissions for Product.

        :note:: Initial Django Permission (add, change, delete, view) are added.
        """
        permissions = (
            ('change_price_product', 'Can change price of a product'),
        )

    def __str__(self):
        return self.name

    def get_unit_display(self):
        if self.unit is not None:
            return self.unit.lower()
        else:
            return 'unit'

    def get_upper_unit_display(self):
        if self.unit is None:
            return 'Unit'
        elif self.unit == 'G':
            return 'Kg'
        elif self.unit == 'CL':
            return 'L'

    def get_quantity_display(self, value):
        if self.unit:
            if self.unit == 'CL':
                if value >= 100:
                    return str(round(value / 100, 2)) + 'L'
                else:
                    return str(round(value, 0)) + 'cl'
            if self.unit == 'G':
                if value >= 1000:
                    return str(round(value / 1000, 2)) + 'kg'
                else:
                    return str(round(value, 0)) + 'g'
        else:
            if value > 1:
                return str(round(value, 0)) + ' produits'
            else:
                return str(round(value, 0)) + ' produit'

    def get_automatic_price(self):
        """
        Return the price calculated over the last stockentry concerning the product.
        If there is no stock entry realisated, return 0.
        """
        try:
            margin_profit = configuration_get('MARGIN_PROFIT').get_value()

            last_stockentry = self.stockentryproduct_set.order_by(
                '-stockentry__datetime').first()
            if last_stockentry is not None:
                return round(decimal.Decimal(last_stockentry.unit_price() * self.correcting_factor * decimal.Decimal(1 + margin_profit / 100)), 4)
            else:
                return 0
        except IndexError:
            return decimal.Decimal(0)

    def deviating_price_from_auto(self):
        automatic_price = self.get_automatic_price()
        if automatic_price == 0:
            return 0
        else:
            return round((self.manual_price - automatic_price) / automatic_price * 100, 4)

    def get_price(self):
        """
        Return price for product, depending on is_manual
        """
        if self.is_manual:
            return self.manual_price
        else:
            return self.get_automatic_price()

    def get_strategy_display(self):
        if self.is_manual:
            return 'manuel'
        else:
            return 'automatique'

    def last_inventoryproduct(self, offset=0):
        """
        Return the last inventoryproduct of the current product.
        Return None if there is no inventory.
        """
        try:
            list_inventoryproduct = self.inventoryproduct_set.all()
            if list_inventoryproduct is None:
                return None
            else:
                return list_inventoryproduct.order_by('-id')[0+offset]
        except IndexError:
            return None

    def last_inventoryproduct_value(self, offset=0):
        try:
            return self.last_inventoryproduct(offset).quantity
        except AttributeError:
            return decimal.Decimal(0)

    def sales_since_last_inventory(self, offset=0):
        """
        Return all SaleProduct concerning the product since the last inventory.
        """
        try:
            return self.saleproduct_set.filter(
                sale__datetime__gte=self.last_inventoryproduct(offset).inventory.datetime)
        except AttributeError:
            return self.saleproduct_set.all()

    def stockentries_since_last_inventory(self, offset=0):
        """
        Return all StockEntryProduct concerning the product since the last inventory
        """
        try:
            last_inventory = self.last_inventoryproduct(
                offset).inventory.datetime
            return self.stockentryproduct_set.filter(stockentry__datetime__gte=last_inventory)
        except AttributeError:
            return self.stockentryproduct_set.all()

    def current_stock_estimated(self, offset=0):
        """
        Calculate the theorical stock since the last inventory.
        Used in order to modify the correcting_factor comparing this value with
        the value given by the next inventory.
        """
        stock_base = self.last_inventoryproduct_value(offset)
        stock_input = sum(
            se.quantity for se in self.stockentries_since_last_inventory(offset))
        stock_output = sum(
            s.quantity for s in self.sales_since_last_inventory(offset))
        corrected_stock_output = stock_output * \
            decimal.Decimal(self.correcting_factor)

        return stock_base + stock_input - corrected_stock_output

    def get_current_stock_estimated_display(self, offset=0):
        """
        Return the current stock estimated using human units
        cl -> L (if more than 1 L)
        g -> KG (if more than 1 KG)
        unit -> unit
        """
        current_stock_estimated = self.current_stock_estimated(offset)

        # If negative stock, display 0
        if current_stock_estimated < 0:
            return self.get_quantity_display(0)

        return self.get_quantity_display(current_stock_estimated)

    def update_correcting_factor(self, next_stock):
        """
        Calculate the corrected correcting_factor comparing the next stock and
        the one currently calculated.
        estimated_stock = last_inventory + input - output_estimated
        real_stock = last_inventory + input - output_real
        diff = input_estimated - input_real
        estimated_stock - real_stock = last_inventory + input - output_estimated - last_inventory - input + output_real
        estimated_stock - real_stock = output_real - output_estimated
        I need: estimated_stock - real_stock = 0
        => output_real = output_estimated
        output_real = sales * correcting_factor
        correcting_factor = output_real / sales
        correcting_factor = (last_inventory + input - real_stock) / sales

        If no sales are registered since the last inventory (stock_output = 0),
        don't update the correcting factor (it should tend to infinity).
        It appends when ZeroDivisionError is raised.
        """
        stock_base = self.last_inventoryproduct_value(1)
        stock_input = sum(
            se.quantity for se in self.stockentries_since_last_inventory(1))
        stock_output = sum(
            s.quantity for s in self.sales_since_last_inventory(1))

        try:
            self.correcting_factor = decimal.Decimal(
                (stock_base + stock_input - next_stock) / stock_output
            )
            self.save()
        except (ZeroDivisionError, decimal.DivisionByZero, decimal.DivisionUndefined, decimal.InvalidOperation):
            pass
