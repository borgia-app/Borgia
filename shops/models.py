#-*- coding: utf-8 -*-
from django.db.models import Q
from django.db.models import Model
from contrib.models import TimeStampedDescription
from django.utils.timezone import now

from finances.models import *
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from settings_data.models import Setting


class Shop(models.Model):
    """Le magasin ("shop") est l'objet qui possede les contenants ou les produits unitaire.

        :Example:

        le foyer
        l'auberge
    """

    # Atttributs
    name = models.CharField('Nom', max_length=255, default="Shop name")
    description = models.TextField('Description', default="Description")

    # Méthodes
    def __str__(self):
        return self.name

    def list_product_base_single_product(self, status_sold="both"):
        """
        Renvoie une liste contenant les produits de base avec les différentes quantités disponibles,
        vendu ou non selon le paramètre status_sold
        qui sont dans le shop
        qui sont des singles products
        :param status_sold:
        :return une liste contenant des (produit_base, quantités)
        """

        list_product_base_single_product = []
        for e in ProductBase.objects.all():
            if status_sold is False and SingleProduct.objects.filter(product_base=e, is_sold=False,
                                                                     product_base__shop=self).exists():
                list_product_base_single_product.append((e,
                                                         SingleProduct.objects.filter(product_base=e, is_sold=False,
                                                                                      product_base__shop=self)))
            elif status_sold is True and SingleProduct.objects.filter(product_base=e, is_sold=True,
                                                                      product_base__shop=self).exists():
                list_product_base_single_product.append((e,
                                                         SingleProduct.objects.filter(product_base=e, is_sold=True,
                                                                                      product_base__shop=self)))
            elif status_sold is "both":
                list_product_base_single_product.append((e, SingleProduct.objects.filter(product_base=e,
                                                                                         product_base__shop=self)))
        return list_product_base_single_product

    def list_product_base_container(self, type, status_sold="both"):
        """
        Renvoie une liste contenant les produits de base avec les différentes quantités disponibles,
        vendu ou non selon le paramètre status_sold
        qui sont dans le shop
        qui sont des containers
        qui sont dans les types listés dans "type"
        :param status_sold:
        :param type:
        :return:
        """
        list_product_base_container = []
        for e in ProductBase.objects.all():
            if status_sold is False and Container.objects.filter(product_base=e, is_sold=False, product_base__shop=self,
                                                                 product_base__product_unit__type=type).exists():
                list_product_base_container.append((e, Container.objects.filter(product_base=e, is_sold=False,
                                                                                product_base__shop=self,
                                                                                product_base__product_unit__type=type)))

            elif status_sold is True and Container.objects.filter(product_base=e, is_sold=True, product_base__shop=self,
                                                                  product_base__product_unit__type=type).exists():
                list_product_base_container.append((e,Container.objects.filter(product_base=e, is_sold=True,
                                                                               product_base__shop=self,
                                                                               product_base__product_unit__type=type)))
            elif status_sold is "both":
                list_product_base_container.append((e, Container.objects.filter(product_base=e,
                                                                                product_base__shop=self,
                                                                                product_base__product_unit__type=type)))
        return list_product_base_container

    class Meta:
        permissions = (
            ('reach_workboard_foyer', 'Aller sur le workboard du foyer'),
            ('sell_foyer', 'Vendre des produits au foyer'),
            ('reach_workboard_auberge', 'Aller sur le workboard de l\'auberge'),
            ('sell_auberge', 'Vendre des produits à l\'auberge'),
        )


class ProductBase(models.Model):
    """

    """
    # Listes de validations
    TYPE_CHOICES = (('single_product', 'Produit unitaire'), ('container', 'Conteneur'))

    # Attributs
    name = models.CharField('Nom', max_length=255, default="Product base name")
    description = models.TextField('Description', default="Description")
    is_manual = models.BooleanField('Gestion manuelle du prix', default=False)
    manual_price = models.DecimalField('Prix manuel', default=0, decimal_places=2, max_digits=9,
                                       validators=[MinValueValidator(Decimal(0))])
    brand = models.CharField('Marque', max_length=255)
    type = models.CharField('Type', max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])

    quantity = models.DecimalField('Quantité d\'unité de produit', default=0, null=True, blank=True, decimal_places=2,
                                   max_digits=9, validators=[MinValueValidator(Decimal(0))])
    # Relations
    # Avec shops.models
    shop = models.ForeignKey('Shop')
    product_unit = models.ForeignKey('ProductUnit', related_name='product_unit', blank=True, null=True)
    is_active = models.BooleanField('Actif', default=True)

    # Méthodes
    def __str__(self):
        if self.quantity and self.product_unit:
            return self.name + ' ' + str(self.quantity) + ' ' + self.product_unit.unit
        else:
            return self.name

    def calculated_price_usual(self):
        if self.type == 'container':
            # Il faut round la fraction (sinon 2/3 = ...)
            # Il faut en plus round  à 2 chiffres Decimal * Decimal
            # Car 1,50 * 2,00 = 3,0000 sinon
            return round((self.set_calculated_price_mean() * self.product_unit.usual_quantity()) / self.quantity, 2)
        else:
            return self.set_calculated_price_mean()

    def set_calculated_price_mean(self):
        """
        Calcule le prix de vente du produit de base en faisant une moyenne sur les produits encore en stock, non vendu
        :return:
        """
        try:
            sum_prices = 0
            if self.type == 'container':
                instances_products = Container.objects.filter(product_base=self, quantity_remaining__isnull=False)
            else:
                instances_products = SingleProduct.objects.filter(product_base=self, is_sold=False)

            for i in instances_products:
                sum_prices += i.price

            calculated_price = round(sum_prices / len(instances_products), 2)

            try:
                margin_profit = Setting.objects.get(name='MARGIN_PROFIT').get_value()
            except ObjectDoesNotExist:
                margin_profit = 0
            calculated_price += calculated_price * Decimal(margin_profit / 100)

            return round(calculated_price, 2)
        except ZeroDivisionError:
            return 0
        except InvalidOperation:
            return 0

    def manual_price_usual(self):
        try:
            if self.type == 'container':
                return round((self.manual_price * self.product_unit.usual_quantity()) / self.quantity, 2)
            else:
                return self.manual_price
        except AttributeError:
            return 0

    def get_moded_usual_price(self):
        if self.is_manual:
            return self.manual_price_usual()
        else:
            return self.calculated_price_usual()

    def get_moded_price(self):
        if self.is_manual:
            return self.manual_price
        else:
            return self.set_calculated_price_mean()

    def deviating_price_from_auto(self):
        try:
            return round((abs(self.set_calculated_price_mean() - self.manual_price) / self.set_calculated_price_mean())*100, 2)
        except ZeroDivisionError:
            return None
        except InvalidOperation:
            return None

    def quantity_products_stock(self):
        """
        Retourne la quantité de produits non vendus héritants de ce produit de base dans le stock
        """
        return SingleProduct.objects.filter(product_base=self, is_sold=False).count() \
               + Container.objects.filter(product_base=self, is_sold=False).count()

    class Meta:
        permissions = (
            ('list_productbase', 'Lister les produits de base'),
            ('retrieve_productbase', 'Afficher un produit de base'),
            ('change_price_productbase', 'Changer le prix d\'un produit de base'),
        )


class SingleProduct(models.Model):
    """Le produit unitaire ("single product") est un objet indivisible.
    Cette classe représente un objet physique qui est un jour passé entre les mains de l'association
    Diverses informations viennent de ProductBase, mais le prix est ici

    :Example:

    une bouteille de biere de 33cl
    une casquette
    """

    # Attributs
    price = models.DecimalField('Prix d\'achat', default=0, decimal_places=2, max_digits=9,
                                validators=[MinValueValidator(Decimal(0))])
    sale_price = models.DecimalField('Prix de vente', default=0, decimal_places=2, max_digits=9, null=True, blank=True,
                                     validators=[MinValueValidator(Decimal(0))])
    purchase_date = models.DateField('Date d\'achat', default=now)
    expiry_date = models.DateField('Date d\'expiration', blank=True, null=True)
    place = models.CharField('Lieu de stockage', max_length=255)
    is_sold = models.BooleanField('Est vendu', default=False)

    # Relations
    # Avec shops.models
    product_base = models.ForeignKey('ProductBase', related_name='product_base_single_product')
    # Avec finances.models
    sale = models.ForeignKey('finances.Sale', null=True, blank=True)

    # Méthodes
    def __str__(self):
        return self.product_base.__str__() + ' n°' + str(self.pk)

    class Meta:
        permissions = (
            ('list_singleproduct', 'Lister les produits unitaires'),
            ('retrieve_singleproduct', 'Afficher un produit unitaire')
        )


class Container(models.Model):
    """Le contenant ("container") est un produit qui contient x unites d'un autre produit: c'est un emballage.
    Les contenants sont souvents consignes.
    Cette classe représente un objet physique qui est un jour passé entre les mains de l'association
    Diverses informations viennent de ProductBase, mais le prix est ici

    :Example:

    un fut de biere contient 15, 30, etc. litres de biere.
    """

    # Attributs
    price = models.DecimalField('Prix d\'achat', default=0, decimal_places=2, max_digits=9,
                                validators=[MinValueValidator(Decimal(0))])
    purchase_date = models.DateField('Date d\'achat', default=now)
    expiry_date = models.DateField('Date d\'expiration', blank=True, null=True)
    place = models.CharField('Lieu de stockage', max_length=255)

    # Devenu obsolète
    quantity_remaining = models.DecimalField('Quantité d\'unité produit restante', default=0, decimal_places=2, max_digits=9,
                                             validators=[MinValueValidator(Decimal(0))])

    is_sold = models.BooleanField('Est vendu', default=False)
    # TODO: gestion des consignes

    # Relations
    # Avec shops.models
    product_base = models.ForeignKey('ProductBase', related_name='product_base_container')

    # Méthodes
    def __str__(self):
        return self.product_base.__str__() + ' ' + str(self.pk)

    def quantity_sold(self):
        quantity_sold = 0
        for product in SingleProductFromContainer.objects.filter(container=self):
            quantity_sold += product.quantity
        return quantity_sold

    def estimated_quantity_remaining(self):
        quantity = self.product_base.quantity - self.quantity_sold()
        pourcentage = (quantity / self.product_base.quantity) * 100
        return quantity, round(pourcentage)

    class Meta:
        permissions = (
            ('list_container', 'Lister les conteneurs'),
            ('retrieve_container', 'Afficher un conteneur'),
            ('change_active_keg', 'Changer le fut d\'une tireuse'),
        )


class ProductUnit(models.Model):
    """Unite de produit.

    :Example:

    un centilitre pour les liquides
    un gramme pour les fromages
    """

    # Listes de validations
    UNIT_CHOICES = (('CL', 'cl'), ('G', 'g'), ('CENT', 'cent'))
    TYPE_CHOICES = (('keg', 'fût'), ('liquor', 'alcool fort'), ('syrup', 'sirop'), ('soft', 'soft'),
                    ('food', 'alimentaire'), ('meat', 'viande'), ('cheese', 'fromage'), ('side', 'accompagnement'),
                    ('fictional_money', 'argent fictif'))

    # Attributs
    name = models.CharField('Nom', max_length=255, default="Product unit name")
    description = models.TextField('Description', max_length=255, null=True, blank=True)
    unit = models.CharField('Unité', max_length=255, choices=UNIT_CHOICES, default=UNIT_CHOICES[0][0])
    type = models.CharField('Type', max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])

    is_active = models.BooleanField('Actif', default=True)

    # Méthodes
    def usual_quantity(self):
        if self.type in ('keg', 'soft'):
            return 25
        elif self.type in ('liquor', 'syrup'):
            return 4
        elif self.type in ('meat', 'cheese', 'side'):
            return 1

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('list_productunit', 'Lister les unités de produits'),
            ('retrieve_productunit', 'Afficher une unité de produit'),
        )


class SingleProductFromContainer(models.Model):
    """
    Produit unique cree à partir d'un container
    par exemple : un verre de X product unit d'un container
    """

    # Attributs
    quantity = models.IntegerField('Quantité d\'unité de produit', default=0, validators=[MinValueValidator(Decimal(0))])
    sale_price = models.DecimalField('Prix de vente', default=0, decimal_places=2, max_digits=9,
                                     validators=[MinValueValidator(Decimal(0))])

    # Relations
    container = models.ForeignKey('Container')
    sale = models.ForeignKey('finances.Sale', null=True, blank=True)

    def __str__(self):
        return self.container.product_base.product_unit.__str__() + ' ' + \
               str(self.quantity) + self.container.product_base.product_unit.get_unit_display()
