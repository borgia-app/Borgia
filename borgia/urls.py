#-*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import logout, login

from borgia.views import LoginPG


urlpatterns = [
    # Applications
    url(r'^admin/', admin.site.urls),
    url(r'^users/', include('users.urls')),
    url(r'^finances/', include('finances.urls')),
    url(r'^shops/', include('shops.urls')),
    url(r'notifications/', include('notifications.urls')),
    url(r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog', name='jsi18n_catalog'),

    # Authentification
    url(r'^$', login, {'template_name': 'login.html'}, name='url_login'),  # A rediriger vers /auth/login
    url(r'^auth/login', login, {'template_name': 'login.html'}, name='url_login'),
    url(r'^auth/logout', logout, {'template_name': 'logout.html', 'next_page': login}),

    # Alias url pour PGs
    url('^(?P<organe>\w+)$', LoginPG.as_view(), name='url_login_pg')
]
