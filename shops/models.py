from django.utils.timezone import now

from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator

from finances.models import *
from settings_data.models import Setting


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

    def __str__(self):
        return self.name

    def get_display_type(self):
        if self.unit is not None:
            return 'Vente au ' + self.get_unit_display()
        else:
            return 'Vente à l\'unité'

    def get_automatic_price(self):
        return Decimal(0)

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
            return 'l'
