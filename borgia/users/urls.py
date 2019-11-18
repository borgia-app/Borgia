from django.urls import include, path

from users.views import (GroupUpdateView, UserAddByListXlsxDownload,
                         UserCreateView, UserDeactivateView, UserListView,
                         UserRetrieveView, UserUpdateView,
                         UserUploadXlsxView, balance_from_username,
                         username_from_username_part)

users_patterns = [
    path('users/', include([
        path('', UserListView.as_view(), name='url_user_list'),
        path('create/', UserCreateView.as_view(), name='url_user_create'),
        path('<int:user_pk>/', include([
            path('', UserRetrieveView.as_view(), name='url_user_retrieve'),
            path('update/', UserUpdateView.as_view(), name='url_user_update'),
            path('deactivate/', UserDeactivateView.as_view(), name='url_user_deactivate')
        ])),

        path('add_by_list/xlsx/', UserUploadXlsxView.as_view(), name='url_add_by_list_xlsx'),
        path('add_by_list/xlsx/download/', UserAddByListXlsxDownload.as_view(), name='url_add_by_list_xlsx_download')
    ])),
    path('groups/<int:group_pk>/update/', GroupUpdateView.as_view(), name='url_group_update'),
    path('ajax/username_from_username_part/', username_from_username_part, name='url_ajax_username_from_username_part'),
    path('ajax/balance_from_username/', balance_from_username, name='url_balance_from_username')
]
