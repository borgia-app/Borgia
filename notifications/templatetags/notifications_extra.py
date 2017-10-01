from django import template
from notifications.models import *
from django.template import Template, Context

register = template.Library()


@register.simple_tag(takes_context=True)
def html_rendering_tag(context, notification):
    """
    A tag to process template display of notifications.
    :param context: the context used to determine session values such as "group_name"
    :param notification: a notification object to render
    :return: a string
    """
    try:
        notification_template = NotificationTemplate.objects.get(notification_class=notification.notification_class,
                                                                 target_users=notification.target_category,
                                                                 target_groups=notification.group_category,
                                                                 is_activated=True)

        if (notification.target_category == "ACTOR") or (notification.target_category == "RECIPIENT"):
            return Template(template_rendering_engine(notification_template.xml_template)).render(template.Context({
                'recipient': notification.action_medium_object,
                'object': notification.action_medium_object,
                'actor': notification.actor_object,
                'target_object': notification.target_object,
                'group_name': context['group_name'],
            }))
        elif context['user'] in User.objects.filter(groups=notification.group_category.notificationgroup):
            return Template(template_rendering_engine(notification_template.xml_template)).render(template.Context({
                                'recipient': notification.action_medium_object,
                                'object': notification.action_medium_object,
                                'actor':   notification.actor_object,
                                'target_object': notification.target_object,
                                'group_name': context['group_name'],
                                }))
        else:
            return "Il devrait y avoir une notification ici," \
                   " mais tu ne fais plus parti du groupe auquel elle était destinée"
    except ObjectDoesNotExist:
        return "Il devrait y avoir une notification ici," \
               " elle a été désactivée ou son public a été modifié"

@register.simple_tag(takes_context=True)
def notification_icon(context, notification):
    """
    A tag to generate font awesome icon depending on notification's type.
    :param notification: a notification object
    :return: a string (icon class)
    """

    if (notification.type == "SUCCESS"):
        return "fa-check-circle"
    elif notification.type == "WARNING":
        return "fa-exclamation-circle"
    elif notification.type == "DANGER":
        return "fa-ban"
    else:
        return "fa-info-circle"
