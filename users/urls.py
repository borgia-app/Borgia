#-*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.views import password_change, password_change_done
from users.views import *
from django.contrib.auth.decorators import permission_required
from borgia.views import *


urlpatterns = [
    # Permission dans la vue
    url(r'^manage_group$', ManageGroupView.as_view(), name='url_manage_group'),
    url(r'^profile/$', profile_view, name='url_profile'),
    url(r'^create/', permission_required('users.add_user', raise_exception=True)
    (UserCreateView.as_view()), name='url_create_user'),
    # Permission dans la vue
    url(r'^retrieve/(?P<pk>\d+)/$', UserRetrieveView.as_view(), name='url_retrieve_user'),
    # Permission dans la vue
    url(r'^update/(?P<pk>\d+)/$', UserUpdateView.as_view(), name='url_update_user'),
    url(r'^update/admin/(?P<pk>\d+)/$', permission_required('users.change_user', raise_exception=True)
    (UserUpdateAdminView.as_view()), name='url_update_admin_user'),
    url(r'^desactivate/(?P<pk>\d+)/$', permission_required('users.delete_user', raise_exception=True)
    (UserDesactivateView.as_view()), name='url_desactivate_user'),
    #url(r'^$', permission_required('users.list_user', raise_exception=True)
    #(UserListView.as_view()), name='url_list_user'),
    #url(r'^list_complete$', permission_required('users.list_user', raise_exception=True)
    #(UserListCompleteView.as_view()), name='url_list_user_complete'),

    # Ajax
    url(r'^username_from_username_part$', username_from_username_part, name='url_username_from_username_part'),
    url(r'^data_from_username', permission_required('shops.sell_foyer' or 'shops.sell_auberge' or 'shops.sell_cvis' or 'shops.sell_bkars', raise_exception=True)
        (data_from_username), name='url_data_from_username'),

    # Token
    url(r'^token/link_token_user$', permission_required('users.link_token_user', raise_exception=True)
        (LinkTokenUserView.as_view()), name='url_link_token_user'),

    # Workboards
    url(r'^presidents/workboard$', permission_required('users.reach_workboard_presidents', raise_exception=True)
        (workboard_presidents), name='url_workboard_presidents'),
    url(r'^vices_presidents_vie_interne/workboard$', permission_required('users.reach_workboard_vices_presidents_vie_interne', raise_exception=True)
        (workboard_vices_presidents_vie_interne), name='url_workboard_vices_presidents_vie_interne'),

    url(r'^user/$', permission_required('users.list_user', raise_exception=True)
        (UserListView.as_view()), name='url_list_user'),

    # REST
    url(r'^user/get/$', permission_required('users.list_user', raise_exception=True)
        (get_list_model), {'model': User, 'search_in': ['username', 'last_name', 'first_name', 'family']}, name='url_get_list_user'),
    url(r'^user/get/retrieve/(?P<pk>\d+)/$', permission_required('users.list_user', raise_exception=True)
        (get_unique_model), {'model': User}, name='url_get_retrieve_user'),
]
