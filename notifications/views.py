#-*- coding: utf-8 -*-

from django.views.generic import ListView
from notifications.models import *
from contrib.models import add_to_breadcrumbs
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from borgia.models import ListCompleteView
from notifications.forms import notiftest

# CRUD modèle notification

# List


class NotificationListView(ListCompleteView):
    form_class = notiftest
    template_name = 'notifications/notification_list.html'
    success_url = '/auth/login'
    attr = {
        'order_by': '-creation_datetime',
        }

    def get(self, request, *args, **kwargs):
        # Ajout au fil d'ariane
        add_to_breadcrumbs(request, 'Notifications')
        return super(NotificationListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        # Récupération de la liste de notifications filtrées de l'user
        self.query = Notification.objects.filter(target_user=self.request.user).order_by(self.attr['order_by'])
        for notification in self.query:
            if notification.read_date is None:
                notification.read_date = now()
                notification.save()
        return super(NotificationListView, self).get_context_data(**kwargs)


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

