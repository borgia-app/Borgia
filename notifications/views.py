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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# CRUD modèle notification

# List


class NotificationListView(ListCompleteView):
    form_class = notiftest
    template_name = 'notifications/notification_list.html'
    success_url = '/auth/login'
    attr = {
        'order_by': '-creation_datetime',
        }
    paginate_by = 25

    def get(self, request, *args, **kwargs):
        # Ajout au fil d'ariane
        add_to_breadcrumbs(request, 'Notifications')
        return super(NotificationListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Récupération du contexte depuis la super-classe
        context \
            = super(NotificationListView, self).get_context_data(**kwargs)

        # Récupération de la liste de notifications filtrées de l'user
        query_supply = Notification.objects.filter(target_user=self.request.user).order_by(self.attr['order_by'])

        # Pagination
        notifications_list_paginator = Paginator(query_supply, self.paginate_by, orphans=0, allow_empty_first_page=True)
        context['paginator'] = notifications_list_paginator
        # Filtre de la page à afficher en fonction de la requête
        page = self.request.GET.get('page')
        if page == 'last':
            # If page is 'last', deliver first page.
            page = notifications_list_paginator.num_pages
        elif page == 'first':
            # If page is 'first', deliver first first.
            page = 1
        try:
            notifications_list_page = notifications_list_paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = 1
            notifications_list_page = notifications_list_paginator.page(page)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = notifications_list_paginator.num_pages
            notifications_list_page = notifications_list_paginator.page(page)
        context['page'] = notifications_list_page

        page_links = []
        for page_number in notifications_list_paginator.page_range:
            if (int(page) - 1) <= page_number <= (int(page) + 1):
                page_links.append(page_number)
        context['page_links'] = page_links
        return context


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

