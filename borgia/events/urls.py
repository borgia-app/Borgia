from django.urls import include, path

from events.views import (EventChangeWeight, EventCreate, EventDelete,
                          EventDownloadXlsx, EventFinish, EventList,
                          EventManageUsers, EventRemoveUser,
                          EventSelfRegistration, EventUpdate, EventUploadXlsx)

events_patterns = [
    path('events/', include([
        path('', EventList.as_view(), name='url_event_list'),
        path('create/', EventCreate.as_view(), name='url_event_create'),
        path('<int:pk>/', include([
            path('update/', EventUpdate.as_view(), name='url_event_update'),
            path('finish/', EventFinish.as_view(), name='url_event_finish'),
            path('delete/', EventDelete.as_view(), name='url_event_delete'),
            path('self_registration/', EventSelfRegistration.as_view(), name='url_event_self_registration'),
            path('users/', EventManageUsers.as_view(), name='url_event_manage_users'),
            path('users/<user_pk>/remove/', EventRemoveUser.as_view(), name='url_event_remove_user'),
            path('users/<int:user_pk>/change_weight', EventChangeWeight.as_view(), name='url_event_change_weight'),
            path('xlsx/download/', EventDownloadXlsx.as_view(), name='url_event_download_xlsx'),
            path('xlsx/upload/', EventUploadXlsx.as_view(), name='url_event_upload_xlsx')
        ]))
    ]))
]
