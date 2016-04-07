#-*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import logout, login, password_reset, password_reset_complete, password_reset_confirm

from borgia.views import LoginPG, jsi18n_catalog


urlpatterns = [
    # Applications
    url(r'^admin/', admin.site.urls),
    url(r'^users/', include('users.urls')),
    url(r'^finances/', include('finances.urls')),
    url(r'^shops/', include('shops.urls')),
    url(r'notifications/', include('notifications.urls')),
    url(r'^local/jsi18n$', jsi18n_catalog),

    # Authentification
    url(r'^$', login, {'template_name': 'login.html'}, name='url_login'),  # A rediriger vers /auth/login
    url(r'^auth/login', login, {'template_name': 'login.html'}, name='url_login'),
    url(r'^auth/logout', logout, {'template_name': 'logout.html', 'next_page': login}, name='url_logout'),
    url(r'^auth/password_reset$', password_reset, {'template_name': 'password_reset_form.html',
                                                   'email_template_name': 'password_reset_email.html',
                                                   'subject_template_name': 'password_reset_subject.html',
                                                   'post_reset_redirect': '/auth/login'}, name='url_password_reset'),
    url(r'^auth/password_reset/confirm$', password_reset_confirm, {'template_name': 'password_reset_confirm.html'},
        name='url_password_reset_confirm'),
    # url(r'^auth/password_reset/done$', password_reset_done, name='url_password_reset_done'),
    url(r'^auth/password_reset/complete$', password_reset_complete, {'template_name': 'password_reset_complete.html'},
        name='url_password_reset_complete'),

    # Alias url pour PGs
    url('^(?P<organe>\w+)$', LoginPG.as_view(), name='url_login_pg')
]
