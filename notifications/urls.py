#-*- coding: utf-8 -*-
from django.conf.urls import url

from notifications.views import *


urlpatterns = [

    # Model notification
    url(r'^create/$', NotificationCreateView.as_view(), name='url_create_notification'),  # C
    url(r'^retrieve/(?P<pk>\d+)/$', NotificationRetrieve.as_view(), name='url_retrieve_notification'),  # R
    url(r'^update/(?P<pk>\d+)/$', NotificationUpdateView.as_view(), name='url_update_notification'),  # U
    url(r'^delete/(?P<pk>\d+)/$', NotificationDeleteView.as_view(), name='url_delete_bank_account'),  # D
    url(r'^$', NotificationListView.as_view(), name='url_list_notification'),  # Liste

]
