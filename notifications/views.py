#-*- coding: utf-8 -*-

from django.views.generic import ListView
from notifications.models import *
from contrib.models import add_to_breadcrumbs

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

