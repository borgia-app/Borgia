#-*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import logout, login


urlpatterns = [
    # Applications
    url(r'^admin/', admin.site.urls),
    url(r'^users/', include('users.urls')),
    url(r'^finances/', include('finances.urls')),
    url(r'^shops/', include('shops.urls')),

    # Authentification
    url(r'^$', login, {'template_name': 'login.html'}, name='url_login'), # A rediriger vers /auth/login
    url(r'^auth/login', login, {'template_name': 'login.html'}, name='url_login'),
    url(r'^auth/logout', logout, {'template_name': 'logout.html', 'next_page': login}),
]
