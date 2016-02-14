#-*- coding: utf-8 -*-
from django.db.models import Q
from django.db.models import Model
from contrib.models import TimeStampedDescription

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
            if status_sold is False:
                list_product_base_single_product.append((e,
                                                         SingleProduct.objects.filter(product_base=e, is_sold=False,
                                                                                      shop=self)))
            elif status_sold is True:
                list_product_base_single_product.append((e,
                                                         SingleProduct.objects.filter(product_base=e, is_sold=True,
                                                                                      shop=self)))
            else:
                list_product_base_single_product.append((e, SingleProduct.objects.filter(product_base=e, shop=self)))
        return list_product_base_single_product

    def list_product_base_container(self, status_sold="both", type=ProductUnit.TYPE_CHOICES):
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
            if status_sold is False:
                list_product_base_container.append((e, Container.objects.filter(product_base=e, is_sold=False,
                                                                                shop=self,
                                                                                product_unit__type__in=type)))
            elif status_sold is True:
                list_product_base_container.append((e,Container.objects.filter(product_base=e, is_sold=True,
                                                                               shop=self,
                                                                               product_unit__type__in=type)))
            else:
                list_product_base_container.append((e, Container.objects.filter(product_base=e, shop=self,
                                                                                product_unit__type__in=type)))
        return list_product_base_container


class ProductBase(models.Model):
    """

    """
    # Listes de validations
    TYPE_CHOICES = (('single_product', 'Produit unitaire'), ('container', 'Conteneur'))

    # Attributs
    name = models.CharField(max_length=255, default="Product base name")
    description = models.TextField()
    calculated_price = models.FloatField(default=0)
    brand = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])
    
    # Relations
    # Avec shops.models
    shop = models.ForeignKey('Shop')

    # Méthodes
    def __str__(self):
        return self.name


class SingleProduct(ProductBase):
    """Le produit unitaire ("single product") est un objet indivisible.
    Cette classe représente un objet physique qui est un jour passé entre les mains de l'association
    Diverses informations viennent de ProductBase, mais le prix est ici

    :Example:

    une bouteille de biere de 33cl
    une casquette
    """

    # Attributs
    price = models.FloatField(default=0)
    purchase_date = models.DateField(default=now)
    expiry_date = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=255)
    is_sold = models.BooleanField(default=False)

    # Relations
    # Avec shops.models
    product_base = models.ForeignKey('ProductBase')
    # Avec finances.models
    # purchase = models.ForeignKey('finances.Purchase', null=True, blank=True)

    # Méthodes
    def __str__(self):
        return self.product_base.__str__() + str(self.pk)


class Container(ProductBase):
    """Le contenant ("container") est un produit qui contient x unites d'un autre produit: c'est un emballage.
    Les contenants sont souvents consignes.
    Cette classe représente un objet physique qui est un jour passé entre les mains de l'association
    Diverses informations viennent de ProductBase, mais le prix est ici

    :Example:

    un fut de biere contient 15, 30, etc. litres de biere.
    """

    # Attributs
    price = models.FloatField(default=0)
    purchase_date = models.DateField(default=now)
    expiry_date = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=255)
    quantity = models.FloatField(default=0)
    quantity_remaining = models.FloatField(default=0)
    # TODO: gestion des consignes

    # Relations
    # Avec shops.models
    product_base = models.ForeignKey('ProductBase')
    product_unit = models.ForeignKey('ProductUnit')
    # Avec finances.models

    # Méthodes
    def __str__(self):
        return self.product_unit.__str__() + self.product_base.__str__() + str(self.pk)

    def clean(self):
        if self.quantity_remaining is None:
            self.quantity_remaining = self.quantity
        return super(Container, self).clean()

    def pourcentage_quantity_remaining(self):
        return (self.quantity_remaining / self.quantity) * 100


class ProductUnit(models.Model):
    """Unite de produit.

    :Example:

    un centilitre pour les liquides
    un gramme pour les fromages
    """

    # Listes de validations
    UNIT_CHOICES = (('CL', 'cl'), ('G', 'g'))
    TYPE_CHOICES = (('keg', 'fut'), ('liquor', 'alcool fort'), ('syrup', 'sirop'), ('soft', 'soft'))

    # Attributs
    name = models.CharField(max_length=255, default="Product unit name")
    description = models.TextField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=255, choices=UNIT_CHOICES, default=UNIT_CHOICES[0][0])
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0])

    # Méthodes
    def usual_quantity(self):
        if self.type is "keg" or "soft":
            return 25
        elif self.type is "liquor" or "syrup":
            return 4


class SingleProductFromContainer(models.Model):
    """
    Produit unique cree à partir d'un container
    par exemple : un verre de X product unit d'un container
    """
    container = models.ForeignKey('Container')
    quantity = models.IntegerField()
    price = models.FloatField()
    purchase = models.ForeignKey('finances.Purchase')

    def nb_glass(self):
        return int(self.quantity/25)


