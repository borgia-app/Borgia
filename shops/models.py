from django.db import models
from django.utils.timezone import now

from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, MinValueValidator

from settings_data.models import Setting
from stocks.models import InventoryProduct, StockEntryProduct
from finances.models import SaleProduct


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

    class Meta:
        """
        Define Permissions for Shop.

        :note:: Initial Django Permission (create, delete, change) are added.
        """
        permissions = (
            # CRUDL
            # add_shop
            # change_shop
            # delete_shop
            ('list_shop', 'Lister les magasins'),
            ('retrieve_shop', 'Afficher les détails d\'un magasin'),

            # Product management
            ('list_product', 'Lister les produits'),
            ('retrieve_product', 'Afficher les détails d\'un produit'),
            ('change_price_product', 'Changer le prix d\'un produit'),
            ('change_stock_product', 'Régulariser le stock d\'un produit'),
        )


class Product(models.Model):
    UNIT_CHOICES = (('CL', 'cl'), ('G', 'g'))
    name = models.CharField('Nom', max_length=255)
    is_manual = models.BooleanField('Gestion manuelle du prix', default=False)
    manual_price = models.DecimalField('Prix manuel', default=0,
                                       decimal_places=2, max_digits=9,
                                       validators=[
                                           MinValueValidator(Decimal(0))])
    shop = models.ForeignKey(
        'Shop',
        related_name='%(app_label)s_%(class)s_shop',
        on_delete=models.CASCADE)
    is_active = models.BooleanField('Actif', default=True)
    unit = models.CharField('Unité', max_length=255, choices=UNIT_CHOICES, blank=True, null=True)
    correcting_factor = models.DecimalField('Facteur correcteur de ventes', default=1,
                                       decimal_places=4, max_digits=9,
                                       validators=[
                                           MinValueValidator(Decimal(0))])

    def __str__(self):
        return self.name

    def get_display_type(self):
        if self.unit is not None:
            return 'Vente au ' + self.get_unit_display()
        else:
            return 'Vente à l\'unité'

    def get_automatic_price(self):
        """
        Return the price calculated over the last stockentry concerning the product.
        """
        try:
            try:
                margin_profit = Setting.objects.get(name='MARGIN_PROFIT').get_value()
            except ObjectDoesNotExist:
                margin_profit = 0

            last_stockentry = sorted(StockEntryProduct.objects.filter(product=self), key=lambda x: x.stockentry.datetime, reverse=True)[0]
            return round(Decimal(last_stockentry.unit_price() * Decimal(1 + margin_profit / 100)), 4)
        except IndexError:
            return Decimal(0)

    def deviating_price_from_auto(self):
        automatic_price = self.get_automatic_price()
        if automatic_price == 0:
            return 0
        else:
            return round(( self.manual_price - automatic_price) / automatic_price * 100 , 4)

    def get_price(self):
        if self.is_manual:
            return self.manual_price
        else:
            return self.get_automatic_price()

    def get_display_price(self):
        if self.unit:
            return str(self.get_price()) + '€ / ' + self.upper_quantity()
        else:
            return str(self.get_price()) + '€ / produit'

    def get_display_price_with_strategy(self):
        if self.is_manual:
            return self.get_display_price() + ' (manuel)'
        else:
            return self.get_display_price() + ' (automatique)'

    def upper_quantity(self):
        if self.unit == 'G':
            return 'kg'
        elif self.unit == 'CL':
            return 'L'

    def last_inventoryproduct(self, offset=0):
        """
        Return the last inventoryproduct of the current product.
        Return None if there is no inventory.
        """
        try:
            return sorted(InventoryProduct.objects.filter(product=self), key=lambda x: x.inventory.datetime, reverse=True)[0+offset]
        except IndexError:
            return None

    def last_inventoryproduct_value(self, offset=0):
        try:
            return self.last_inventoryproduct(offset).quantity
        except AttributeError:
            return Decimal(0)

    def sales_since_last_inventory(self, offset=0):
        """
        Return all SaleProduct concerning the product since the last inventory.
        """
        try:
            return SaleProduct.objects.filter(
                product=self,
                sale__datetime__gte=self.last_inventoryproduct(offset).inventory.datetime
                )
        except AttributeError:
            return SaleProduct.objects.filter(
                product=self
            )

    def stockentries_since_last_inventory(self, offset=0):
        """
        Return all StockEntryProduct concerning the product since the
        """
        try:
            return StockEntryProduct.objects.filter(
                product=self,
                stockentry__datetime__gte=self.last_inventoryproduct(offset).inventory.datetime
            )
        except AttributeError:
            return StockEntryProduct.objects.filter(
                product=self
            )

    def current_stock_estimated(self, offset=0):
        """
        Calculate the theorical stock since the last inventory.
        Used in order to modify the correcting_factor comparing this value with
        the value given by the next inventory.
        """
        stock_base = self.last_inventoryproduct_value(offset)
        stock_input = sum(se.quantity for se in self.stockentries_since_last_inventory(offset))
        stock_output = sum(s.quantity for s in self.sales_since_last_inventory(offset))
        corrected_stock_output = stock_output * Decimal(self.correcting_factor)

        return stock_base + stock_input - corrected_stock_output

    def get_current_stock_estimated_display(self, offset=0):
        """
        Return the current stock estimated using human units
        cl -> L (if more than 1 L)
        g -> KG (if more than 1 KG)
        unit -> unit
        """
        current_stock_estimated = self.current_stock_estimated(offset)
        return self.get_quantity_display(current_stock_estimated)

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
                return str(round(value, 0)) + 'produit'

    def update_correcting_factor(self, next_stock):
        """
        Calculate the corrected correcting_factor comparing the next stock and
        the one currently calculated.
        estimated_stock = last_inventory + input - output_estimated
        real_stock = last_inventory + input - output_real
        diff = input_estimated - input_real
        estimated_stock - real_stock = last_inventory + input - output_estimated - last_inventory - input + output_real
        estimated_stock - real_stock = output_real - output_estimated
        je veux estimated_stock - real_stock = 0
        => output_real = output_estimated
        output_real = sales * correcting_factor
        correcting_factor = output_real / sales
        correcting_factor = (last_inventory + input - real_stock) / sales
        """
        stock_base = self.last_inventoryproduct_value(1)
        stock_input = sum(se.quantity for se in self.stockentries_since_last_inventory(1))
        stock_output = sum(s.quantity for s in self.sales_since_last_inventory(1))
        self.correcting_factor = Decimal(
            (stock_base + stock_input - next_stock) / stock_output
        )
        self.save()
