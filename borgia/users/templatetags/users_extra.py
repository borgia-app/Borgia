from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

from borgia.utils import group_name_display
from configurations.utils import configuration_get

register = template.Library()


@register.filter()
def has_perm(user, permission_required):
    return user.has_perm(permission_required)


@register.filter(name='get_transaction_model')
def get_transaction_model(transaction):
    return transaction.__class__.__name__

@register.filter(name='get_transaction_label')
def get_transaction_label(transaction):
    name = transaction.__class__.__name__
    if name == "Event":
       return ("Evénement",
               transaction.description.capitalize() + ' le ' + transaction.date.strftime("%d %h %Y"))
    elif name == "Recharging":
       recharging_solution = transaction.content_solution.__class__.__name__
       label = recharging_solution
       if recharging_solution == 'Lydia':
          label += " n°"+ transaction.content_solution.id_from_lydia
       elif recharging_solution == 'Cheque':
          label += " n°" + transaction.content_solution.cheque_number
       return ("Rechargement", label)
    elif name == "Transfert":
       return ("Transfert",
         'De ' + transaction.sender.__str__() +
         ' à ' + transaction.recipient.__str__() +
         ', '+ transaction.justification
       )
    elif name == "Sale":
       return ("Achat"+" "+ transaction.shop.name,
               transaction.string_products())
    elif name == "ExceptionnalMovement":
       return ("Mouvement exceptionnel", 'De '+transaction.operator.__str__()+' le '+ transaction.datetime.strftime("%d %h %Y"))

@register.inclusion_tag('breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    try:
        display_breadcrumbs = context['request'].session['breadcrumbs'][:]
        last_one = display_breadcrumbs[len(display_breadcrumbs)-1]
        del display_breadcrumbs[len(display_breadcrumbs)-1]
        display_breadcrumbs.append((last_one[0], 'last'))
        return {'breadcrumbs': display_breadcrumbs}
    except KeyError:
        pass
    except IndexError:
        pass


@register.filter()
@stringfilter
def order_by(attr, request):
    """
    Ce tag permet de créer la variable de tri en fonction des paramètres de tri actuels.
    Si on triait déjà par "attr" (car order_by=attr), alors on vient trier par "-attr"
    """
    if request.GET.get('order_by') == attr:
        return '-' + attr
    else:
        return attr


@register.simple_tag
def get_center_name():
    return configuration_get('CENTER_NAME').get_value()

@register.simple_tag
def set_default_template():
    default_template = getattr(settings, "DEFAULT_TEMPLATE", None)
    if default_template:
        return 'less/_bootstrap-' + default_template + '.less'
    else:
        return 'less/_bootstrap-light.less'

@register.simple_tag
def set_template(template_name):
    default_template = getattr(settings, "DEFAULT_TEMPLATE", None)
    if template_name:
        return 'less/_bootstrap-' + template_name + '.less'
    elif default_template:
        return 'less/_bootstrap-' + default_template + '.less'
    else:
        return 'less/_bootstrap-light.less'

@register.simple_tag
def set_brand(template_name):
    default_template = getattr(settings, "DEFAULT_TEMPLATE", None)
    if template_name:
        return 'img/borgia-logo-' + template_name + '.png'
    elif default_template:
        return 'img/borgia-logo-' + default_template + '.png'
    else:
        return 'img/borgia-logo-light.png'

@register.filter
def group_name(group):
    return group_name_display(group)
