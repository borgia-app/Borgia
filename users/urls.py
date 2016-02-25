#-*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.views import password_change, password_change_done
from users.views import *
from django.contrib.auth.decorators import permission_required


urlpatterns = [
    # Permission dans la vue
    url(r'^manage_group$', ManageGroupView.as_view(), name='url_manage_group'),
    url(r'^password_change$', password_change, {'template_name': 'users/password_change.html',
                                                'post_change_redirect': password_change_done}, name='password_change'),
    url(r'^password_change_done$', password_change_done, {'template_name': 'users/password_change_done.html'}),
    url(r'^profile/$', profile_view, name='url_profile'),
    url(r'^create/', permission_required('users.add_user', raise_exception=True)
    (UserCreateView.as_view()), name='url_create_user'),
    # Permission dans la vue
    url(r'^retrieve/(?P<pk>\d+)/$', UserRetrieveView.as_view(), name='url_retrieve_user'),
    # Permission dans la vue
    url(r'^update/(?P<pk>\d+)/$', UserUpdateView.as_view(), name='url_update_user'),
    url(r'^delete/(?P<pk>\d+)/$', permission_required('users.delete_user', raise_exception=True)
    (UserDeleteView.as_view()), name='url_delete_user'),
    url(r'^$', permission_required('users.list_user', raise_exception=True)
    (UserListView.as_view()), name='url_list_user'),

    # Ajax
    url(r'^username_from_username_part$', username_from_username_part, name='url_username_from_username_part')
]
