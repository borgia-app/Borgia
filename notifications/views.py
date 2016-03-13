#-*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse, force_text
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView
from django.core.urlresolvers import reverse
from datetime import datetime
from notifications.models import *

# CRUD modèle notification

# Create


class NotificationCreateView(CreateView):
    model = Notification
    fields = ['type','actor_type', 'actor_id', 'verb', 'target_user', 'action_medium_type', 'action_medium_id', 'target_type', 'target_id']
    template_name = 'notifications/notification_create.html'

    def get_success_url(self):
        return reverse('url_retrieve_notification', kwargs={'pk' : str(self.object.pk)})

# Retreive


class NotificationRetrieve(DeleteView):
    model = Notification
    template_name = 'notifications/notification_retrieve.html'

# Update


class NotificationUpdateView(UpdateView):
    model = Notification
    fields = ['type', 'actor_type', 'actor_id', 'verb', 'target_user', 'action_medium_type', 'action_medium_id', 'target_type', 'target_id', 'is_displayed', 'displayed_date', 'is_readed', 'readed_date']
    template_name = 'notifications/notification_update.html'

    def get_success_url(self):
        return reverse('url_retrieve_notification', args=str(self.object.pk))

# Delete


class NotificationDeleteView(DeleteView):
    model = Notification
    template_name = "notifications/notification_delete.html"
    success_url = '/notifications/'

# List


class NotificationListView(ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    queryset = Notification.objects.all()

