#-*- coding: utf-8 -*-
from django.conf.urls import url

from notifications.views import *
from django.contrib.auth.decorators import permission_required


urlpatterns = [

    # Model notification
    url(r'^$', NotificationListCompleteView.as_view(), name='url_list_complete_notification'),  # Liste
    url(r'^read_notification/$', read_notification, name='url_read_notification'),
    url(r'^templates/$',
        permission_required('notifications.notification_templates_manage', raise_exception=True)(NotificationTemplateListCompleteView.as_view()),
        name='url_list_complete_notification_template'),
    url(r'^templates/update/(?P<pk>\d+)/$',
        permission_required('notifications.notification_templates_manage', raise_exception=True)(NotificationTemplateUpdateView.as_view()),
        name='url_update_notification_template'),

]
