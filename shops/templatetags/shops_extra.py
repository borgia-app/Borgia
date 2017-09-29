from django import template
from shops.models import Product

register = template.Library()


@register.simple_tag()
def multiply(a, b, *args, **kwargs):
    return a * b


@register.simple_tag()
def divide(a, b, *args, **kwargs):
    return a / b
