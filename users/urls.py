from django.urls import include, path

from users.views import (ManageGroupView, UserSelfUpdateView, UserCreateView,
                         UserDeactivateView, UserListView, UserRetrieveView,
                         UserSelfDeactivateView, UserUpdateView,
                         balance_from_username, username_from_username_part)

users_patterns = [
    path('<str:group_name>/users/', include([
        path('', UserListView.as_view(), name='url_user_list'),
        path('create/', UserCreateView.as_view(), name='url_user_create'),
        path('<int:pk>/', include([
            path('', UserRetrieveView.as_view(), name='url_user_retrieve'),
            path('update/', UserUpdateView.as_view(), name='url_user_update'),
            path('deactivate/', UserDeactivateView.as_view(), name='url_user_deactivate'),
            path('self_deactivate/', UserSelfDeactivateView.as_view(), name='url_self_deactivate'),
        ])),
        path('self/', UserSelfUpdateView.as_view(), name='url_user_self_update')
    ])),
    path('<str:group_name>/groups/<int:pk>/update/', ManageGroupView.as_view(), name='url_group_update'),
    path('ajax/username_from_username_part/', username_from_username_part, name='url_ajax_username_from_username_part'),
    path('ajax/balance_from_username/', balance_from_username, name='url_balance_from_username')
]
