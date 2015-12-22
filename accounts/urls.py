from django.conf.urls import url
from django.contrib.auth.views import login, logout, password_change, password_change_done
from accounts.views import profile_view, change_informations_view, UserCreateView, UserUpdateView
from django.contrib.auth.decorators import permission_required, login_required


urlpatterns = [
    # Authentification
    url(r'^login', login, {'template_name': 'accounts/login.html'}),
    url(r'^logout', logout, {'template_name': 'accounts/logout.html', 'next_page': login}),

    # Password
    url(r'^password_change', password_change, {'template_name': 'accounts/password_change.html',
                                               'post_change_redirect': password_change_done}, name='password_change'),
    url(r'^password_change_done', password_change_done, {'template_name': 'accounts/password_change_done.html'}),

    # Profile
    url(r'^profile', profile_view, name='url_profile'),

    # Administration
    url(r'^user_create', permission_required('accounts.add_user')(UserCreateView.as_view()), name='url_create_user'),
    url(r'^user_update/(?P<pk>\d+)/$', UserUpdateView.as_view(), name='url_update_user'),

]
