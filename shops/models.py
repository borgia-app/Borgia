#-*- coding: utf-8 -*-
from django.db.models import Q
from django.db.models import Model
from contrib.models import TimeStampedDescription
from django.utils.timezone import now

from finances.models import *


class Shop(models.Model):
    """Le magasin ("shop") est l'objet qui possede les contenants ou les produits unitaire.

        :Example:

        le foyer
        l'auberge
    """

    # Atttributs
    name = models.CharField(max_length=255, default="Shop name")
    description = models.TextField()

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
        )


class ProductBase(models.Model):
    """

    """
    # Listes de validations
    TYPE_CHOICES = (('single_product', 'Produit unitaire'), ('container', 'Conteneur'))

    # Attributs
    name = models.CharField(max_length=255, default="Product base name")
    description = models.TextField()
    calculated_price = models.DecimalField(default=0, decimal_places=2, max_digits=9)
    brand = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])

    quantity = models.DecimalField(default=0, null=True, blank=True, decimal_places=2, max_digits=9)

    # Relations
    # Avec shops.models
    shop = models.ForeignKey('Shop')
    product_unit = models.ForeignKey('ProductUnit', related_name='product_unit', blank=True, null=True)

    # Méthodes
    def __str__(self):
        if self.quantity:
            return self.name + ' ' + str(self.quantity) + ' ' + self.product_unit.unit
        else:
            return self.name

    def calculated_price_usual(self):
        if self.quantity is not None:
            # Il faut round la fraction (sinon 2/3 = ...)
            # Il faut en plus round  à 2 chiffres Decimal * Decimal
            # Car 1,50 * 2,00 = 3,0000 sinon
            return round(round((self.product_unit.usual_quantity() / self.quantity), 2) * self.calculated_price, 2)
        else:
            return self.calculated_price

    class Meta:
        permissions = (
            ('list_productbase', 'Lister les produits de base'),
            ('retrieve_productbase', 'Afficher un produit de base')
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
    price = models.DecimalField(default=0, decimal_places=2, max_digits=9)
    sale_price = models.FloatField(null=True, blank=True)
    purchase_date = models.DateField(default=now)
    expiry_date = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=255)
    is_sold = models.BooleanField(default=False)

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
    price = models.DecimalField(default=0, decimal_places=2, max_digits=9)
    purchase_date = models.DateField(default=now)
    expiry_date = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=255)
    quantity_remaining = models.DecimalField(default=0, decimal_places=2, max_digits=9)
    is_sold = models.BooleanField(default=False)
    # TODO: gestion des consignes

    # Relations
    # Avec shops.models
    product_base = models.ForeignKey('ProductBase', related_name='product_base_container')
    # Avec finances.models

    # Méthodes
    def __str__(self):
        return self.product_base.__str__() + ' ' + str(self.pk)

    def clean(self):
        if self.quantity_remaining is None:
            self.quantity_remaining = self.product_base.quantity
        return super(Container, self).clean()

    def pourcentage_quantity_remaining(self):
        return (self.quantity_remaining / self.product_base.quantity) * 100

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
    TYPE_CHOICES = (('keg', 'fut'), ('liquor', 'alcool fort'), ('syrup', 'sirop'), ('soft', 'soft'),
                    ('fictional_money', 'fictional money'))

    # Attributs
    name = models.CharField(max_length=255, default="Product unit name")
    description = models.TextField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=255, choices=UNIT_CHOICES, default=UNIT_CHOICES[0][0])
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])

    # Méthodes
    def usual_quantity(self):
        if self.type in ('keg', 'soft'):
            return 25
        elif self.type in ('liquor', 'syrup'):
            return 4

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
    quantity = models.IntegerField(default=0)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=9)

    # Relations
    container = models.ForeignKey('Container')
    sale = models.ForeignKey('finances.Sale')

    def __str__(self):
        return self.container.product_base.product_unit.__str__() + ' ' +\
               str(self.quantity) + self.container.product_base.product_unit.unit

