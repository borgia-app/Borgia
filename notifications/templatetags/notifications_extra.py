from django import template
from notifications.models import *
from django.template import Template, Context

register = template.Library()

# TODO : commenter la méthode notifications


@register.filter(name='filter_get_unread_notifications_for_user')
def filter_get_unread_notifications_for_user(request):
    get_unread_notifications_for_user(request)

    return ""  # Nécessaire sinon retourne un beau none dans le html


@register.simple_tag(takes_context=True)
def html_rendering_tag(context, notification):

    return Template(template_rendering_engine(notification.notification_template.message)).render(template.Context({
                        'recipient': notification.action_medium_object,
                        'object': notification.action_medium_object,
                        'actor':   notification.actor_object,
                        'group_name': context['group_name'],
                        }))
