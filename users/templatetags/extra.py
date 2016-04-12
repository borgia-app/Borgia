from django import template
from django.contrib.auth.models import Group
from django.template.defaultfilters import stringfilter

register = template.Library()

# TODO: commenter ce templatetag

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


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
