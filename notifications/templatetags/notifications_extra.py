from django import template
from notifications.models import *

register = template.Library()

# TODO : commenter la méthode notifications


@register.filter(name='filter_get_unread_notifications_for_user')
def filter_get_unread_notifications_for_user(request):
    get_unread_notifications_for_user(request)

    return ""  # Nécessaire sinon retourne un beau none dans le html


