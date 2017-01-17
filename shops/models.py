from django.db.models import Q
from django.db.models import Model
from contrib.models import TimeStampedDescription
from django.utils.timezone import now

from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

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
    :type name: string
    :type description: string

    :note:: TODO: Add module attributes.
    """
    name = models.CharField('Nom', max_length=255, default="Shop name")
    description = models.TextField('Description', default="Description")

    def __str__(self):
        """
        Return the display name.

        :returns: name attribute
        :rtype: string
        """
        return self.name

    def list_product_base_single_product(self, status_sold="both"):
        """
        Return the list of ProductBase corresponding to SingleProduct of this
        Shop and the corresponding instances (sold of not) of each
        SingleProduct. Shooters are excluded, refer to method
        list_product_base_single_product_shooter

        :param status_sold: if True return only sold instances, if False only
        not sold instances, both if "both".
        :type status_sold: string, must be in [False, True, "both"], default
        "both"

        :returns: list of tuples (ProductBase object, SingleProduct list
        objects).
        :rtype: list of tuples, ProductBase object (index 0 of each tuple),
        SingleProduct list objects (index 1 of each tuple)

        :note:: False or True for status_sold are boolean, but both is string.
        Python types are dynamics.
        """
        list_product_base_single_product = []
        for e in ProductBase.objects.filter(type='single_product').exclude(description__contains='shooter'):
            if status_sold is False and SingleProduct.objects.filter(
                product_base=e,
                is_sold=False,
                product_base__shop=self).exclude(
                    product_base__description__contains="shooter").exists():
                list_product_base_single_product.append(
                    (
                        e,
                        SingleProduct.objects.filter(product_base=e,
                                                     is_sold=False,
                                                     product_base__shop=self)
                        )
                    )
            elif status_sold is True and SingleProduct.objects.filter(
                product_base=e,
                is_sold=True,
                product_base__shop=self).exclude(
                    product_base__description__contains="shooter").exists():
                list_product_base_single_product.append(
                    (
                        e,
                        SingleProduct.objects.filter(
                            product_base=e,
                            is_sold=True,
                            product_base__shop=self)
                        )
                    )
            elif status_sold is "both":
                list_product_base_single_product.append(
                    (
                        e,
                        SingleProduct.objects.filter(
                            product_base=e,
                            product_base__shop=self)
                        )
                    )
        return list_product_base_single_product

    def list_product_base_single_product_shooter(self, status_sold="both"):
        """
        Return the list of ProductBase corresponding to SingleProduct of this
        Shop and the corresponding instances (sold of not) of each
        SingleProduct. Only Shooters instances here.

        :param status_sold: if True return only sold instances, if False only
        not sold instances, both if "both".
        :type status_sold: string, must be in [False, True, "both"], default
        "both"

        :returns: list of tuples (ProductBase object, SingleProduct list
        objects).
        :rtype: list of tuples, ProductBase object (index 0 of each tuple),
        SingleProduct list objects (index 1 of each tuple)

        :note:: False or True for status_sold are boolean, but both is string.
        Python types are dynamics.
        :note:: We should add an attribute in ProductBase or SingleProduct
        models in order to filter shooters, not only in description!
        """
        list_product_base_shooter = []
        for e in ProductBase.objects.filter(description__contains='shooter', type='single_product'):
            if status_sold is False and SingleProduct.objects.filter(
                product_base=e,
                is_sold=False,
                product_base__shop=self).exists():
                    list_product_base_shooter.append(
                        (
                            e,
                            SingleProduct.objects.filter(
                                product_base=e,
                                is_sold=False,
                                product_base__shop=self)
                            )
                        )
            elif status_sold is True and SingleProduct.objects.filter(
                product_base=e,
                is_sold=True,
                product_base__shop=self).exists():
                    list_product_base_shooter.append(
                        (
                            e,
                            SingleProduct.objects.filter(
                                product_base=e,
                                is_sold=True,
                                product_base__shop=self)
                            )
                        )
            elif status_sold is "both":
                list_product_base_shooter.append(
                    (
                        e,
                        SingleProduct.objects.filter(
                            product_base=e,
                            product_base__shop=self)
                        )
                    )
        return list_product_base_shooter

    def list_product_base_container(self, type, status_sold="both"):
        """
        Return the list of Container corresponding to SingleProduct of this
        Shop and the corresponding instances (sold of not) of each
        Container.

        :param status_sold: if True return only sold instances, if False only
        not sold instances, both if "both".
        :param type: type of ProductUnit corresponding to the ProductBase.
        :type status_sold: string, must be in [False, True, "both"], default
        "both"
        :type type: string must be in TYPE_CHOICES of ProductUnit

        :returns: list of tuples (ProductBase object, Container list
        objects).
        :rtype: list of tuples, ProductBase object (index 0 of each tuple),
        Container list objects (index 1 of each tuple)

        :note:: False or True for status_sold are boolean, but both is string.
        Python types are dynamics.
        """
        list_product_base_container = []
        for e in ProductBase.objects.filter(type='container', product_unit__type=type):
            if status_sold is False and Container.objects.filter(
                product_base=e,
                is_sold=False,
                product_base__shop=self,
                product_base__product_unit__type=type).exists():
                    list_product_base_container.append(
                        (
                            e,
                            Container.objects.filter(
                                product_base=e,
                                is_sold=False,
                                product_base__shop=self,
                                product_base__product_unit__type=type)
                            )
                        )
            elif status_sold is True and Container.objects.filter(
                product_base=e,
                is_sold=True,
                product_base__shop=self,
                product_base__product_unit__type=type).exists():
                    list_product_base_container.append(
                        (
                            e,
                            Container.objects.filter(
                                product_base=e,
                                is_sold=True,
                                product_base__shop=self,
                                product_base__product_unit__type=type)
                            )
                        )
            elif status_sold is "both":
                list_product_base_container.append(
                    (
                        e,
                        Container.objects.filter(
                            product_base=e,
                            product_base__shop=self,
                            product_base__product_unit__type=type)
                        )
                    )
        return list_product_base_container

    class Meta:
        """
        Define Permissions for Shop.

        :note:: Initial Django Permission (create, delete, change) are added.
        """
        permissions = (
            ('sell_foyer', 'Vendre des produits au foyer'),
            ('sell_auberge', 'Vendre des produits à l\'auberge'),
            ('sell_cvis', 'Vendre des produits à la cvis'),
            ('sell_bkars', 'Vendre des produits à la bb'),
            ('add_product', 'Ajouter des produits'),
            ('list_product', 'Lister les produits'),
            ('change_price_product', 'Changer le prix des produits'),
        )


class ProductBase(models.Model):
    """
    Define a base of product.

    This base let us derive several instances of products, by models Container
    and SingleProduct. Then ProductBase is just a base, you should have only
    one instance of each ProductBase object, however to represent each instance
    you can of course have a lot of instances of Container and SingleProduct.

    :note:: Should be Abstract Model ?

    :param name: name of the ProductBase, same as instances, mandatory.
    :param description: description of the ProductBase, same as instances,
    mandatory.
    :param is_manual: true if you want to set the sell price manually,
    mandatory.
    :param manual_price: the price set manually. If is_manual is true this is
    the sell price, if it's set to false, it is the last manual price saved,
    mandatory.
    WARNING: It stands for the whole ProductBase instance, refer to notes.
    :param brand: brand of the ProductBase, same as instances, mandatory.
    :param type: define the category of the ProductBase, same as instances,
    mandatory.
    Mostly define model of instances of this ProductBase.
    :param quantity: quantity of ProductUnit (set by product_unit) in this
    Product. Not mandatory for SingleProduct ProductBase.
    :param shop: Shop object in which instances of this ProductBase are sold,
    mandatory.
    :param product_unit: ProductUnit object that is in this ProductBase (via
    quantity). Not mandatory for SingleProduct ProductBase.
    :param is_active: If true instances of this ProductBase can be add,
    mandatory.
    :type name: string
    :type description: string
    :type is_manual: boolean, default False
    :type manual_price: float (Decimal), default 0
    :type brand: string
    :type type: string, must be in TYPE_CHOICES, default single_product
    :type quantity: float (Decimal)
    :type shop: Shop object
    :type product_unit: ProductUnit object
    :type is_active: boolean, default True

    :note:: quantity should be integer ?
    :note:: WARNING, the sell price is set for the whole ProductBase, even for
    a Container ProductBase. Because it's the price the buyer knows directly.
    In order to calculate the price for an usual quantity (if needed, for
    instance for Container ProductBase), please refer to methods
    calculated_price_usual and get_moded_price.
    :note:: Even if ProductBases for SingleProduct do not have ProductUnit,
    thus no unit and usual quantity, in some methods, usual quantity refer to
    the quantity of the whole SingleProduct.
    """
    TYPE_CHOICES = (('single_product', 'Produit unitaire'),
                    ('container', 'Conteneur'))

    name = models.CharField('Nom', max_length=255, default="Product base name")
    description = models.TextField('Description', default="Description")
    is_manual = models.BooleanField('Gestion manuelle du prix', default=False)
    manual_price = models.DecimalField('Prix manuel', default=0,
                                       decimal_places=2, max_digits=9,
                                       validators=[
                                           MinValueValidator(Decimal(0))])
    brand = models.CharField('Marque', max_length=255)
    type = models.CharField('Type', max_length=255, choices=TYPE_CHOICES,
                            default=TYPE_CHOICES[0][0])
    quantity = models.DecimalField('Quantité d\'unité de produit', default=0,
                                   null=True, blank=True, decimal_places=2,
                                   max_digits=9, validators=[
                                       MinValueValidator(Decimal(0))])
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    product_unit = models.ForeignKey('ProductUnit',
                                     related_name='product_unit', blank=True,
                                     null=True,
                                     on_delete=models.CASCADE)
    is_active = models.BooleanField('Actif', default=True)

    def __str__(self):
        """
        Return the display name of this ProductBase.

        :returns: string of the name, the quantity and the unit of the
        ProductUnit associated in the case of a ProductBase of Container
        objects. Just name in case of ProductBase of SingleProduct objects.

        :note:: Should be base on type attribute.
        """
        if self.quantity and self.product_unit:
            return (self.name
                    + ' '
                    + str(self.quantity)
                    + ' '
                    + self.product_unit.unit)
        else:
            return self.name

    def calculated_price_usual(self):
        """
        Return the sell price for the usual quantity (Container) or the whole
        SingleProduct, for the automatic price.

        The price is the mean of all buying price of instances for this
        ProductBase object, with a margin profit, please refer to the method
        set_calculated_price_mean.

        :note:: This method is only used to calculate the sell price when the
        attribute manual_price is False.

        :returns: Automatic sell price for an usual quantity of ProductBase in
        case of Container, the whole SingleProduct instead.
        :rtype: float (Decimal)
        """
        if self.type == 'container':
            return round(
                (self.set_calculated_price_mean()
                 * self.product_unit.usual_quantity()) / self.quantity, 2)
        else:
            return self.set_calculated_price_mean()

    def set_calculated_price_mean(self):
        """
        Calculate the mean price of bought product from this ProductBase, which
        are not sold (totally or partially). The margin profit parameter is
        applied here.

        :note:: WARNING, in this method the price stands for the whole
        instance, Container or SingleProduct.

        :returns: Mean bought price of instance from this ProductBase, majored
        with the margin profit parameter.
        :rtype: float (Decimal)
        :note:: In the case where there is no instances not sold, the price
        cannot be set (returns 0). Indeed as ProductBase are not directly sold,
        this case must not be an issue for the user because he is not going to
        see the price 0 as no instances are sold.
        """
        # TODO: verify that we set is_sold=True when quantity_remaining = 0 !
        try:
            sum_prices = 0
            if self.type == 'container':
                instances_products = Container.objects.filter(
                    product_base=self,
                    quantity_remaining__isnull=False,
                    is_sold=False)
            else:
                instances_products = SingleProduct.objects.filter(
                    product_base=self,
                    is_sold=False)

            for i in instances_products:
                sum_prices += i.price

            calculated_price = round(sum_prices / len(instances_products), 2)

            try:
                margin_profit = Setting.objects.get(
                    name='MARGIN_PROFIT').get_value()
            except ObjectDoesNotExist:
                margin_profit = 0
            calculated_price += calculated_price * Decimal(margin_profit / 100)

            return round(calculated_price, 2)
        except ZeroDivisionError:
            return 0
        except InvalidOperation:
            return 0

    def manual_price_usual(self):
        """
        Return the manual price for an usual quantity.

        :returns: Price of an usual quantity sold when is_manual is True.
        :rtype: float (Decimal)

        :note:: In the case of SingleProduct ProductBase, the price is the
        manual price directly.
        """
        # TODO: raise exceptions, don't return 0
        try:
            if self.type == 'container':
                return round(
                    (self.manual_price
                     * self.product_unit.usual_quantity()) / self.quantity, 2)
            else:
                return self.manual_price
        except AttributeError:
            return 0

    def get_moded_usual_price(self):
        """
        Return the sell price for an usual quantity, without knowing if the
        price is set manually of not.

        :returns: sell price for usual quantity
        :rtype: float (Decimal)

        :note:: For the price of the whole instance, please refer to the
        method get_moded_price.
        """
        if self.is_manual:
            return self.manual_price_usual()
        else:
            return self.calculated_price_usual()

    def get_moded_price(self):
        """
        Return the sell price for an instance, without knowing if the price is
        set manually of not.

        :returns: sell price for the whole instance.
        :rtype: float (Decimal)

        :note:: For the price of an usual quantity only, please refer to the
        method get_moded_usual_price.
        """
        if self.is_manual:
            return self.manual_price
        else:
            return self.set_calculated_price_mean()

    def deviating_price_from_auto(self):
        """
        Return the percentage of deviation between the manual price and the
        automatic calculated price.

        :returns: percentage of deviation, from 0 to 100.
        :rtype: float (Decimal)

        :note:: When the automatic calculated price cannot be determined (refer
        to the method set_calculated_price_mean for details), None is returned.
        """
        # TODO: raise exceptions is better
        try:
            return round(
                (abs(self.set_calculated_price_mean()
                     - Decimal(self.manual_price)) / self.set_calculated_price_mean())
                * 100, 2)
        except ZeroDivisionError:
            return None
        except InvalidOperation:
            return None

    def quantity_products_stock(self):
        """
        Return the number of instances of the ProductBase not sold.

        :returns: number of instances.
        :rtype: integer
        """
        return (SingleProduct.objects.filter(
            product_base=self, is_sold=False).count()
            + Container.objects.filter(
                product_base=self, is_sold=False).count())

    class Meta:
        """
        Define Permissions for ProductBase.

        :note:: Initial Django Permission (create, delete, change) are added.
        """
        permissions = (
            ('list_productbase', 'Lister les produits de base'),
            ('retrieve_productbase', 'Afficher un produit de base'),
            ('change_price_productbase',
             'Changer le prix d\'un produit de base'),
        )


class SingleProduct(models.Model):
    """
    Define a SingleProduct.

    This represents a type of instances of ProductBase. This SingleProduct must
    be sold at one and only one time. For instance : a bottle of beer 33cl.
    Moreover this instance will stay in the db forever, even after its sell.
    Then the sell price (which indeed correspond of the price of the Product
    Base at the time t of the same) is saved as an attribute here. The Product
    Base sell price (by get_moded_price and get_moded_usual_price) changes each
    time new instances of SingleProduct or Container are added.

    :param price: buying price of the instance, mandatory.
    :param sale_price: selling price of the instance, only when sold.
    :param purchase_date: date of purchase, mandatory.
    :param expiry_date: date of expiration.
    :param place: place where the instance is conserved before its sell,
    mandatory.
    :param is_sold: true if the instance is sell, mandatory.
    :param product_base: ProductBase parent of the instance, mandatory.
    :param sale: Sale object in which the instance is sold, only when sold.
    :type price: float (Decimal), default 0
    :type sale_price: float (Decimal), default 0
    :type purchase_date: date string, default now
    :type expiry_date: date string
    :type place: string
    :type is_sold: boolean, default False
    :type product_base: ProductBase object
    :type sale: Sale object
    """
    price = models.DecimalField('Prix d\'achat', default=0, decimal_places=2,
                                max_digits=9,
                                validators=[MinValueValidator(Decimal(0))])
    sale_price = models.DecimalField('Prix de vente', default=0,
                                     decimal_places=2, max_digits=9, null=True,
                                     blank=True,
                                     validators=[
                                         MinValueValidator(Decimal(0))])
    purchase_date = models.DateField('Date d\'achat', default=now)
    expiry_date = models.DateField('Date d\'expiration', blank=True, null=True)
    place = models.CharField('Lieu de stockage', max_length=255)
    is_sold = models.BooleanField('Est vendu', default=False)
    product_base = models.ForeignKey(
        'ProductBase', related_name='product_base_single_product',
        on_delete=models.CASCADE)
    sale = models.ForeignKey('finances.Sale', null=True, blank=True,
    on_delete=models.CASCADE)

    def __str__(self):
        """
        Return the display name of this SingleProduct.

        :returns: ProductBase parent display name and id.
        """
        return self.product_base.__str__() + ' n°' + str(self.pk)

    class Meta:
        """
        Define Permissions for Singleproduct.

        :note:: Initial Django Permission (create, delete, change) are added.
        """
        permissions = (
            ('list_singleproduct', 'Lister les produits unitaires'),
            ('retrieve_singleproduct', 'Afficher un produit unitaire')
        )


class Container(models.Model):
    """
    Define a Container.

    This represents a type of instances of ProductBase. This Container must
    be sold by part and several time, until the quantity is null. For instance
    a keg of beer 50000cl. Refer to model SingleProductFromContainer for each
    sold part of this Container.
    Moreover this instance will stay in the db forever, even after its sell.
    Then the sell price (which indeed correspond of the price of the Product
    Base at the time t of the same) is saved as an attribute here. The Product
    Base sell price (by get_moded_price and get_moded_usual_price) changes each
    time new instances of SingleProduct or Container are added.

    :param price: buying price of the instance, mandatory.
    :param purchase_date: date of sell, mandatory.
    :param expiry_date: date of expiration.
    :param place: place where the instance is conserved before its sell,
    mandatory.
    :param quantity_remaining: quantity remaining inside the container at t,
    mandatory.
    :param is_sold: true if the instance is sell, mandatory.
    :param product_base: ProductBase parent of the instance, mandatory.
    :type price: float (Decimal), default 0
    :type purchase_date: date string, default now
    :type expiry_date: date string
    :type place: string
    :type quantity_remaining: float (Decimal), inferior or equal to quantity of
    ProductBase parent, default 0
    :type is_sold: boolean, default False
    :type product_base: ProductBase object

    :note:: The attribute quantity_remaining it out of date now, by the method
    estimated_quantity_remaining.
    """

    # Attributs
    price = models.DecimalField('Prix d\'achat', default=0, decimal_places=2,
                                max_digits=9,
                                validators=[MinValueValidator(Decimal(0))])
    purchase_date = models.DateField('Date d\'achat', default=now)
    expiry_date = models.DateField('Date d\'expiration', blank=True, null=True)
    place = models.CharField('Lieu de stockage', max_length=255)
    quantity_remaining = models.DecimalField(
        'Quantité d\'unité produit restante', default=0, decimal_places=2,
        max_digits=9, validators=[MinValueValidator(Decimal(0))])
    is_sold = models.BooleanField('Est vendu', default=False)
    product_base = models.ForeignKey('ProductBase',
                                     related_name='product_base_container',
                                     on_delete=models.CASCADE)

    def __str__(self):
        """
        Return the display name of this Container.

        :returns: ProductBase parent display name and id.
        """
        return self.product_base.__str__() + ' n°' + str(self.pk)

    def quantity_sold(self):
        """
        Return the quantity sold from the container at time t.

        :returns: quantity sold
        :rtype: float (Decimal)
        """
        quantity_sold = 0
        for product in SingleProductFromContainer.objects.filter(container=self):
            quantity_sold += product.quantity
        return quantity_sold

    def estimated_quantity_remaining(self):
        """
        Estimate the quantity remaining inside the product.

        Indeed this quantity is true regarding the database. However there are
        leaks in the container, thus this quantity cannot be certified.

        :returns: list, quantity remaining (index 0), percentage of the initial
        quantity of ProductBase parent (index 1)
        :rtype: float (Decimal) (index 0), float (Decimal) (index 1)
        """
        quantity = self.product_base.quantity - self.quantity_sold()
        pourcentage = (quantity / self.product_base.quantity) * 100
        return quantity, round(pourcentage, 2)

    class Meta:
        """
        Define Permissions for Container.

        :note:: Initial Django Permission (create, delete, change) are added.
        """
        permissions = (
            ('list_container', 'Lister les conteneurs'),
            ('retrieve_container', 'Afficher un conteneur'),
            ('change_active_keg', 'Changer le fut d\'une tireuse'),
        )


class ProductUnit(models.Model):
    """
    Define a unit of product.

    This unit represents the smallest quantity of a given product. The quantity
    is always 1 for the given unit. For instance, if the ProductUnit has the
    attribute unit = CL, the smallest quantity of this product is 1 cl.

    :param name: name of the ProductUnit, mandatory.
    :param description: description of the ProductUnit.
    :param unit: unit of the 1 smallest quantity of this product, mandatory.
    :param type: information about the category of the ProductUnit, mandatory.
    :param is_active: true if this ProductUnit is active, ie that it could be
    assigned to new Product, mandatory.
    :type name: string
    :type description: string
    :type unit: string, must be in UNIT_CHOICES, default : CL
    :type type: string, must be in TYPE_CHOICES, default: : keg
    :type is_active: boolean

    """
    UNIT_CHOICES = (('CL', 'cl'), ('G', 'g'), ('CENT', 'cent'))
    TYPE_CHOICES = (('keg', 'fût'), ('liquor', 'alcool fort'),
                    ('syrup', 'sirop'), ('soft', 'soft'),
                    ('food', 'alimentaire'), ('meat', 'viande'),
                    ('cheese', 'fromage'), ('side', 'accompagnement'),
                    ('fictional_money', 'argent fictif'))

    name = models.CharField('Nom', max_length=255)
    description = models.TextField('Description', max_length=255, null=True,
                                   blank=True)
    unit = models.CharField('Unité', max_length=255, choices=UNIT_CHOICES,
                            default=UNIT_CHOICES[0][0])
    type = models.CharField('Type', max_length=255, choices=TYPE_CHOICES,
                            default=TYPE_CHOICES[0][0])
    is_active = models.BooleanField('Actif', default=True)

    def usual_quantity(self):
        """
        Return the usual quantity in which the corresponding product is serve,
        regarding its type.

        :returns: integer, the usual quantity.
        """
        if self.type in ('keg', 'soft'):
            return 25
        elif self.type in ('liquor', 'syrup'):
            return 4
        else:
            return 1

    def __str__(self):
        """
        Return the dislayed name of the ProductUnit object.

        :returns: string, name of the ProductUnit object.
        """
        return self.name

    class Meta:
        """
        Define Permissions for ProductUnit.

        :note:: Initial Django Permission (create, delete, change) are added.
        """
        permissions = (
            ('list_productunit', 'Lister les unités de produits'),
            ('retrieve_productunit', 'Afficher une unité de produit'),
        )


class SingleProductFromContainer(models.Model):
    """
    Define a SingleProductFromContainer.

    This model represents a part of a Container, which is sold. Container
    obects are not sold directly, as SingleProduct objects are, you need to
    define a SingleProductFromContainer object which derives from this object
    and select the right quantity.

    :param quantity: Sold quantity, extracted from the Container, mandatory.
    :param sale_price: Price of which the selected quantity is sold, it is the
    price of the ProductBase whose Container derives by get_moded_price,
    mandatory.
    :param container: Container from whose the SingleProductFromContainer is
    extracted, mandatory.
    :param sale: Corresponding sale.
    :type quantity: float (Decimal), default 0
    :type sale_price: float (Decimal), default 0
    :type container: Container object
    :type sale: Sale object

    :note:: Sale should be mandatory ?
    :note:: SingleProducts objects exist directly when they enter the shop.
    However, SingleProductFromContainer are created only when they are sold,
    only the Container exists before the sale.
    """
    quantity = models.IntegerField('Quantité d\'unité de produit', default=0,
                                   validators=[MinValueValidator(Decimal(0))])
    sale_price = models.DecimalField('Prix de vente', default=0,
                                     decimal_places=2, max_digits=9,
                                     validators=[
                                         MinValueValidator(Decimal(0))])
    container = models.ForeignKey('Container', on_delete=models.CASCADE)
    sale = models.ForeignKey('finances.Sale', null=True, blank=True,
    on_delete=models.CASCADE)

    def __str__(self):
        """
        Return the display name.

        :returns: ProductBase of Container display name, quantity extracted
        from the Container and the unit of the ProductBase.
        :rtype: string
        """
        return (self.container.product_base.product_unit.__str__()
                + ' '
                + str(self.quantity)
                + ' '
                + self.container.product_base.product_unit.get_unit_display())
