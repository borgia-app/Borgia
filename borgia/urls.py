from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout

urlpatterns = [
    # Applications
    url(r'^admin/', admin.site.urls),
    url(r'^users/', include('users.urls')),
    url(r'^finances/', include('finances.urls')),

    # Authentification
    url(r'^auth/login', login, {'template_name': 'login.html'}),
    url(r'^auth/logout', logout, {'template_name': 'logout.html', 'next_page': login}),
]
