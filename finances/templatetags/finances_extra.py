from django import template

register = template.Library()


@register.simple_tag
def price_for(sale, user):
    try:
        return sale.price_for(user)
    except AttributeError:
        return 'erreur'


@register.simple_tag
def abs_price_for(sale, user):
    return abs(sale.price_for(user))


@register.simple_tag
def human_reading(value, syst):

    # Transforme les valeurs True / False de done d'un shared event en human
    if syst == 'event_done':
        if value is True:
            return 'Terminé'
        else:
            return 'Non effectué'

    # True -> Oui et False -> Non
    elif syst == 'true_false':
        if value is True:
            return 'Oui'
        else:
            return 'Non'

    # True -> Manuelle et False -> Automatique
    elif syst == 'manual_price':
        if value is True:
            return 'Manuelle'
        else:
            return 'Automatique'

    # Float -> nombre décimal, integer -> entier, boolean -> booleen, string -> chaine de caractères
    elif syst == 'type':
        if value == 'integer':
            return 'nombre entier'
        elif value == 'float':
            return 'nombre décimal'
        elif value == 'string':
            return 'chaîne de caractères'
        elif value == 'boolean':
            return 'booléen (True ou False)'
