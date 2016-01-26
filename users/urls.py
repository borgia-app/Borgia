from django.conf.urls import url
from django.contrib.auth.views import password_change, password_change_done
from users.views import profile_view, UserCreateView, UserUpdatePersoView, UserUpdateAdminView, UserDeleteView, \
    UserRetrieveView, UserListView
from django.contrib.auth.decorators import permission_required


urlpatterns = [
    # Password
    url(r'^password_change$', password_change, {'template_name': 'users/password_change.html',
                                               'post_change_redirect': password_change_done}, name='password_change'),
    url(r'^password_change_done$', password_change_done, {'template_name': 'users/password_change_done.html'}),

    # Profile
    url(r'^profile/$', profile_view, name='url_profile'),

    # Model User (les tests de permissions sont soit dans l'url soit dans le template)
    # Seul ceux qui peuvent add des users
    url(r'^create/', UserCreateView.as_view(), name='url_create_user'),  # C
    # Soit on retrieve soit même, soit on a la permission de tous
    url(r'^retrieve/(?P<pk>\d+)/$', UserRetrieveView.as_view(), name='url_retrieve_user'),  # R
    # Soit on s'update soit même, soit on a la permission de tous
    url(r'^updateP/(?P<pk>\d+)/$', UserUpdatePersoView.as_view(), name='url_updateperso_user'),  # U
    url(r'^updateA/(?P<pk>\d+)/$', permission_required('users.change_user')(UserUpdateAdminView.as_view()),
        name='url_updateadmin_user'),  # U
    # Seul ceux qui peuvent del des users
    url(r'^delete/(?P<pk>\d+)/$', permission_required('users.delete_user')(UserDeleteView.as_view()),
        name='url_delete_user'),  # D
    # Seul ceux qui peuvent list des users
    url(r'^$', permission_required('users.list_user')(UserListView.as_view()), name='url_list_user'),  # Liste
]
