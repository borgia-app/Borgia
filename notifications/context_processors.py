from notifications.models import get_unread_notifications_for_user


def notifications(request):
    """
    Returns a lazy 'notifications' context variable.
    """
    if request.user.is_authenticated():
        return {
            'notifications': get_unread_notifications_for_user(request)
        }
    else:
        return {}