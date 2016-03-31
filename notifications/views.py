#-*- coding: utf-8 -*-

from django.views.generic import ListView, DetailView
from notifications.models import *

# CRUD modèle notification

# List


class NotificationListView(ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'

    def get_queryset(self):
        return Notification.objects.filter(target_user=self.request.user)

