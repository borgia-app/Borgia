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


class Product(TimeStampedDescription):
    """Le produit ("product") est l'objet vendu par l'AE. Il est soit produit unique, soit contenant qui contient
    x unites de produit.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_available_for_sale = models.BooleanField(default=False)
    # Permet de savoir si le produit est disponible a la vente (par exemple un fut de biere peut etre es stock mais
    # conserve pour un evenement a venir)
    is_available_for_borrowing = models.BooleanField(default=False)
    # Permet de savoir si le produit est disponible a l'emprunt
    peremption_date = models.DateField(blank=True, null=True)
    # Un videoprojecteur ne perime pas

    shop = models.ForeignKey('Shop', blank=True, null=True)

    def __str__(self):
        return self.name


class SingleProduct(Product):
    """Le produit unitaire ("single product") est un objet indivisible.

    :Example:

    une bouteille de biere de 33cl
    une casquette
    """

    is_sold = models.BooleanField(default=False)
    price = models.FloatField()
    purchase = models.ForeignKey('finances.Purchase', null=True, blank=True)


class Container(Product):
    """Le contenant ("container") est un produit qui contient x unites d'un autre produit: c'est un emballage.
    Les contenants sont souvents consignes.

    :Example:

    un fut de biere contient 15, 30, etc. litres de biere.
    """
    product_unit = models.ForeignKey('ProductUnit')
    initial_quantity = models.FloatField()
    estimated_remaining_quantity = models.FloatField()
    is_empty = models.BooleanField(default=False)

    opening_date = models.DateField(blank=True, null=True)
    removing_date = models.DateField(blank=True, null=True)

    is_returnable = models.BooleanField()  # Consigne
    value_when_returned = models.FloatField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.product_unit.__str__() + " " + str(self.initial_quantity) + " " + self.product_unit.unit +\
               " n° " + str(self.pk)

    def clean(self):
        if self.estimated_remaining_quantity is None:
            self.estimated_remaining_quantity = self.initial_quantity
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


class Tap(Model):
    number = models.IntegerField()
    container = models.ForeignKey('Container', null=True, blank=True)

    def __str__(self):
        return "Tireuse n° " + str(self.number)
