from django import template
from shops.models import SingleProduct, Container

register = template.Library()


@register.simple_tag()
def multiply(a, b, *args, **kwargs):
    return a * b


@register.simple_tag()
def divide(a, b, *args, **kwargs):
    return a / b


@register.simple_tag
def quantity_stock_product_base(product_base):
    """
    Retourne la quantity en stock des produits héritants du produit de base
    :param product_base: produit de base considéré, instance de ProductBase
    """
    return SingleProduct.objects.filter(product_base=product_base, is_sold=False).count()\
           + Container.objects.filter(product_base=product_base, is_sold=False).count()
