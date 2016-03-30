from django import template

register = template.Library()


@register.simple_tag
def price_for(sale, user):
    try:
        return sale.price_for(user)
    except AttributeError:
        return 'erreur'

@register.simple_tag
def human_reading(value, syst):

    # Transforme les valeurs True / False de done d'un shared event en human
    if syst == 'shared_event_done':
        if value is True:
            return 'Terminé'
        else:
            return 'Non effectué'
