#-*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import logout, login, password_reset, password_reset_complete, password_reset_confirm,\
    password_change, password_change_done, password_reset_done
from borgia.views import LoginPG, page_clean, jsi18n_catalog, TestBootstrapSober, GroupWorkboard
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from users.views import *
from shops.views import ProductList, ProductCreate, ProductDeactivate, ProductRetrieve, ProductUpdate


urlpatterns = [

    url(r'^(?P<group_name>[\w-]+)/workboard/$',
        GroupWorkboard.as_view(), name='url_group_workboard'),

    url(r'^(?P<group_name>[\w-]+)/users/create/$',
        UserCreateView.as_view(), name='url_user_create'),
    url(r'^(?P<group_name>[\w-]+)/users/$',
        UserListView.as_view(), name='url_user_list'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<pk>\d+)/$',
        UserRetrieveView.as_view(), name='url_user_retrieve'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<pk>\d+)/update/$',
        UserUpdateAdminView.as_view(), name='url_user_update'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<pk>\d+)/deactivate/$',
        UserDeactivateView.as_view(), name='url_user_deactivate'),

    url(r'^(?P<group_name>[\w-]+)/users/link_token/$',
        LinkTokenUserView.as_view(), name='url_user_link_token'),
    url(r'^(?P<group_name>[\w-]+)/groups/(?P<pk>\d+)/update/$',
        ManageGroupView.as_view(), name='url_group_update'),

    url(r'^(?P<group_name>[\w-]+)/products/$',
        ProductList.as_view(), name='url_product_list'),
    url(r'^(?P<group_name>[\w-]+)/products/create/$',
        ProductCreate.as_view(), name='url_product_create'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/$',
        ProductRetrieve.as_view(), name='url_product_retrieve'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/update/$',
        ProductUpdate.as_view(), name='url_product_update'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/deactivate/$',
        ProductDeactivate.as_view(), name='url_product_deactivate'),





















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
    url('^(?P<organe>\w+)$', LoginPG.as_view(), name='url_login_pg'),

    # Test Bootstrap CSS & components
    url('^tests/bootstrap$', TestBootstrapSober.as_view()),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Cette ligne permet d'utiliser le dossier MEDIA en
# dev (en prod c'est automatique)
