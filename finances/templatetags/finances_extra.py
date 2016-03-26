from django import template

register = template.Library()


@register.simple_tag
def price_for(sale, user):
    return sale.price_for(user)