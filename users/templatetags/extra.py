from django import template
from django.contrib.auth.models import Group
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


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