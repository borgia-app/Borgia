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

    # Ajax
    url(r'^username_from_username_part$', username_from_username_part, name='url_username_from_username_part'),
    url(r'^balance_from_username', permission_required('shops.sell_auberge', raise_exception=True)
    (balance_from_username), name='url_balance_from_username'),

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
    url(r'^user/api/$', permission_required('users.list_user', raise_exception=True)
    (UserList.as_view()), name='url_api_list_user'),
    url(r'^user/api/unpr/$', UserListUnprotected.as_view(), name='url_api_listunprotected_user'),
    url(r'^user/api/(?P<pk>\d+)/$', permission_required('users.retrieve_user', raise_exception=True)
    (UserDetail.as_view()), name='url_api_retrieveudatedestroy_user'),

]
