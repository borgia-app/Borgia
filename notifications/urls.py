from django.urls import include, path

from notifications.views import (NotificationGroupCreateView,
                                 NotificationGroupListCompleteView,
                                 NotificationGroupUpdateView,
                                 NotificationListCompleteView,
                                 NotificationTemplateCreateView,
                                 NotificationTemplateDeactivateView,
                                 NotificationTemplateUpdateView,
                                 read_notification)

notifications_patterns = [
    path('<str:group_name>/notifications/', include([
        path('', NotificationListCompleteView.as_view(), name='url_notification_list'),
        path('templates/', include([
            path('create/<str:notification_class>/', NotificationTemplateCreateView.as_view(), name='url_notificationtemplate_create'),
            path('<int:pk>/update/', NotificationTemplateUpdateView.as_view(), name='url_notificationtemplate_change'),
            path('<int:pk>/deactivate/', NotificationTemplateDeactivateView.as_view(), name='url_notificationtemplate_deactivate')
        ])),
	    path('groups/', include([
            path('', NotificationGroupListCompleteView.as_view(), name='url_notificationgroup_list'),
            path('create/', NotificationGroupCreateView.as_view(), name='url_notificationgroup_create'),
            path('<int:pk>/update/', NotificationGroupUpdateView.as_view(), name='url_notificationgroup_update')
        ]))
    ])),
    path('ajax/notifications/read_notification/', read_notification, name='url_read_notification')
]
