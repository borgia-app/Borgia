#-*- coding: utf-8 -*-
from django.db.models import Q
from django.db.models import Model
from contrib.models import TimeStampedDescription

from finances.models import *


class Shop(TimeStampedDescription):
    """Le magasin ("shop") est l'objet qui possede les contenants ou les produits unitaire.

        :Example:

        le foyer
        l'auberge
    """

    # Atttributs
    name = models.CharField(max_length=255, default="Shop name")
    description = models.TextField()
    # TODO: ajouter permissions

    # Méthodes
    # TODO: task T57
    def __str__(self):
        return self.name

    def list_single_product(self):
        """
        Renvoie une liste du genre (single product 1), (single product 2) avec les objects directement
        """
        list = []  # Liste de la forme (nom du single product, quantite disponible)
        single_products = SingleProduct.objects.filter(shop=self)

        # Initialisation de la liste
        list.append(single_products[0])

        for sp in single_products:
            in_list = False
            # On regarde si le produit se trouve dejà dans la liste
            for e in list:
                if e.name == sp.name and e.description == sp.description:
                    # Trouve dans la liste
                    in_list = True
                    break
            if in_list == False:
                list.append(sp)

        return list

    def list_single_product_with_qt(self):
        """
        Renvoie une liste du genre (single product 1, qt 1), (single product 2, qt 2)
        """
        list_qt = []  # Liste de la forme (nom du single product, quantite disponible)
        single_products = SingleProduct.objects.filter(shop=self)

        # Initialisation de la liste
        list_qt.append([single_products[1].name, 0])

        for sp in single_products:
            in_list = False
            # On regarde si le produit se trouve dejà dans la liste
            for i, e in enumerate(list_qt):
                if e[0] == sp.name:
                    # Trouve dans la liste
                    in_list = True
                    list_qt[i][1] += 1
                    break
            if in_list == False:
                list_qt.append([sp.name, 1])

        return list_qt

    def list_single_product_name(self):
        """
        Renvoie une liste du genre (single product 1, single product 2)
        Des elements qui n'ont pas une qt nulle (dispo au shop)
        """
        list_name = []
        for e in self.list_single_product_with_qt():
            list_name.append(e[0])

        return list_name

    def list_single_product_with_qt_unsold(self):
        """
        Renvoie une liste du genre (single product 1, qt 1), (single product 2, qt 2)
        """
        list_qt = []  # Liste de la forme (nom du single product, quantite disponible)
        single_products = SingleProduct.objects.filter(Q(shop=self) & Q(is_sold=False))

        # Initialisation de la liste
        if len(single_products) != 0:
            list_qt.append([single_products[0].name, 0])
            for sp in single_products:
                in_list = False
                # On regarde si le produit se trouve dejà dans la liste
                for i, e in enumerate(list_qt):
                    if e[0] == sp.name:
                        # Trouve dans la liste
                        in_list = True
                        list_qt[i][1] += 1
                        break
                if in_list == False:
                    list_qt.append([sp.name, 1])

        return list_qt

    def list_single_product_unsold_name(self):
        """
        Renvoie une liste du genre (single product 1, single product 2)
        Des elements qui n'ont pas une qt nulle (dispo au shop)
        """
        list_name = []
        for e in self.list_single_product_with_qt_unsold():
            list_name.append(e[0])

        return list_name

    def list_single_product_unsold_qt(self):
        """
        Renvoie une liste du genre (qt 1, qt 2)
        Des elements qui n'ont pas une qt nulle (dispo au shop), dans le même ordre que _name
        """
        list_qt = []
        for e in self.list_single_product_with_qt_unsold():
            list_qt.append(e[1])

        return list_qt


class ProductBase(TimeStampedDescription):
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

    # Méthodes
    # TODO: task T59


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
    # purchase = models.ForeignKey('finances.Purchase', null=True, blank=True)

    # Méthodes


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

    # Méthodes
    def __str__(self):
        return self.product_unit.__str__() + " " + str(self.initial_quantity) + " " + self.product_unit.unit +\
               " n° " + str(self.pk)

    def clean(self):
        if self.quantity_remaining is None:
            self.quantity_remaining = self.quantity
        return super(Container, self).clean()

    def pourcentage_estimated_remaining_quantity(self):
        return (self.estimated_remaining_quantity / self.initial_quantity) * 100


class ProductUnit(Product):
    """Unite de produit.

    :Example:

    un centilitre pour les liquides
    un gramme pour les fromages
    """

    price = models.FloatField()
    unit = models.CharField(max_length=10)
    TYPE_CHOICES = (('keg', 'Fût'), ('soft', 'Soft'), ('alcool fort', 'liquor'))
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)

    def price_glass(self):
        return self.price*25

    def price_shoot(self):
        return self.price*4


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


