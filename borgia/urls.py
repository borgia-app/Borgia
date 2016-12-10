#-*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import logout, login, password_reset, password_reset_complete, password_reset_confirm,\
    password_change, password_change_done, password_reset_done
from borgia.views import LoginPG, page_clean, jsi18n_catalog
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Applications
    url(r'^admin/', admin.site.urls),
    url(r'^users/', include('users.urls')),
    url(r'^finances/', include('finances.urls')),
    url(r'^shops/', include('shops.urls')),
    url(r'notifications/', include('notifications.urls')),
    url(r'settings_data/', include('settings_data.urls')),
    url(r'^local/jsi18n$', jsi18n_catalog),

    #Page vide
    url(r'^clean', page_clean, {'template_name': 'page_clean.html'}, name='url_page_clean'),
    # Authentification
    url(r'^$', login, {'template_name': 'login.html'}, name='url_login'),  # A rediriger vers /auth/login
    url(r'^auth/login', login, {'template_name': 'login.html'}, name='url_login'),
    url(r'^auth/logout', logout, {'template_name': 'logout.html', 'next_page': login}, name='url_logout'),

    url(r'^auth/password_reset/$', password_reset, name='reset_password_reset1'),
    url(r'^auth/password_reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^auth/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^auth/done/$', password_reset_complete, name='password_reset_complete'),

    url(r'^auth/password_change$', password_change, {'post_change_redirect': password_change_done}, name='password_change'),
    url(r'^auth/password_change_done$', password_change_done),

    # Alias url pour PGs
    url('^(?P<organe>\w+)$', LoginPG.as_view(), name='url_login_pg')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Cette ligne permet d'utiliser le dossier MEDIA en
# dev (en prod c'est automatique)




