from notifications.models import Notification


def notifications(request):
    """
    Returns a lazy 'notifications' context variable. It contains a queryset with unread notifications (read_datetime
    = None).
    """
    if request.user.is_authenticated():
        return {
            'notifications': Notification.objects.filter(target_user=request.user, read_datetime=None)
        }
    else:
        return {}
