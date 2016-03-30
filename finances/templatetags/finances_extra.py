from django import template

register = template.Library()


@register.simple_tag
def price_for(sale, user):
    try:
        return sale.price_for(user)
    except AttributeError:
        return 'erreur'