#-*- coding: utf-8 -*-
from django.conf.urls import url

from notifications.views import *


urlpatterns = [

    # Model notification
    url(r'^$', NotificationListView.as_view(), name='url_list_notification'),  # Liste

]
