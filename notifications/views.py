#-*- coding: utf-8 -*-

from django.views.generic import ListView
from notifications.models import *
from contrib.models import add_to_breadcrumbs
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse

# CRUD modèle notification

# List


class NotificationListView(ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'

    def get_queryset(self):
        add_to_breadcrumbs(self.request, 'Notifications')
        for e in Notification.objects.filter(target_user=self.request.user):
            if e.read_date is None:
                e.read_date = now()
                e.save()
        return Notification.objects.filter(target_user=self.request.user)  # Récupère toutes les notifications de l'user


def read_notification(request):

    try:
        int(request.GET.get('notification_id'))

        try:
            notification = Notification.objects.get(pk=request.GET.get('notification_id'))
        except Notification.DoesNotExist:
            raise Http404

        if notification.target_user == request.user:

            if notification.read_date is None:
                notification.read_date = now()
                notification.save()

            return HttpResponseRedirect(reverse('url_login'))

        else:
            raise PermissionDenied
    except ValueError:
        raise Http404

