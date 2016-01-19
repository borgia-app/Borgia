from django.db import models
from contrib.models import TimeStampedDescription


class Shop(TimeStampedDescription):
    """Le magasin ("shop") est l'objet qui possede les contenants ou les produits unitaire.

        :Example:

        le foyer
        l'auberge
    """

    def __str__(self):
        return self.name


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


class Container(Product):
    """Le contenant ("container") est un produit qui contient x unites d'un autre produit: c'est un emballage.
    Les contenants sont souvents consignes.

    :Example:

    un fut de biere contient 15, 30, etc. litres de biere.
    """
    product_unit = models.ForeignKey('ProductUnit')
    initial_quantity = models.FloatField()
    estimated_remaining_quantity = models.FloatField(blank=True, null=True)
    is_empty = models.BooleanField(default=False)

    opening_date = models.DateField(blank=True, null=True)
    removing_date = models.DateField(blank=True, null=True)

    is_returnable = models.BooleanField()  # Consigne
    value_when_returned = models.FloatField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)


class ProductUnit(TimeStampedDescription):
    """Unite de produit.

    :Example:

    un centilitre pour les liquides
    un gramme pour les fromages
    """
    price = models.FloatField()
    unit = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    TYPE_CHOICES = (('fût', 'fût'), ('morceau', 'morceau'))
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
