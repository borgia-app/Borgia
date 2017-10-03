from django import template
from django.contrib.auth.models import Group, Permission
from django.template.defaultfilters import stringfilter
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='has_group_perm')
def has_group_perm(group, perm_codename):
    try:
        if (Permission.objects.get(codename=perm_codename)
                in group.permissions.all()):
            return True
        else:
            return False
    except ObjectDoesNotExist:
        return False


@register.filter(name='get_transaction_model')
def get_transaction_model(transaction):
    return transaction.__class__.__name__


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
def center_name():
    return getattr(settings, "CENTER_NAME", None)

@register.simple_tag
def set_template(template):
    default_template = getattr(settings, "DEFAULT_TEMPLATE", None)
    if template:
        return 'less/_bootstrap-' + template + '.less'
    elif default_template:
        return 'less/_bootstrap-' + default_template + '.less'
    else:
        return 'less/_bootstrap-light.less'

@register.simple_tag
def set_brand(template):
    default_template = getattr(settings, "DEFAULT_TEMPLATE", None)
    if template:
        return 'img/borgia-logo-' + template + '.png'
    elif default_template:
        return 'img/borgia-logo-' + default_template + '.png'
    else:
        return 'img/borgia-logo-light.png'
