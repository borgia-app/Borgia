from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from borgia.views import (GadzartsGroupWorkboard, PresidentsGroupWorkboard,
                          ShopGroupWorkboard, TreasurersGroupWorkboard,
                          VicePresidentsInternalGroupWorkboard, handler403,
                          handler404, handler500, jsi18n_catalog)
from finances.urls import finances_patterns
from modules.urls import modules_patterns
from notifications.urls import notifications_patterns
from settings_data.urls import settings_patterns
from shops.urls import shops_patterns
from stocks.urls import stocks_patterns
from users.urls import users_patterns

handler403 = handler403
handler404 = handler404
handler500 = handler500


urlpatterns = [
    # AUTHENTIFICATIONS
    path('', auth_views.LoginView.as_view()),
    path('auth/', include([
        path('login/', auth_views.LoginView.as_view(), name='url_login'),
        path('logout/', auth_views.LogoutView.as_view(), name='url_logout'),

        path('password_change/', auth_views.PasswordChangeView.as_view(),
             name='url_password_change'),
        path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
             name='url_password_change_done'),

        path('password_reset/', auth_views.PasswordResetView.as_view(),
             name='password_reset'),
        path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
             name='password_reset_done'),
        path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
             name='password_reset_confirm'),
        path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
             name='password_reset_complete'),
    ])),
    # WORKBOARDS
    path('presidents/', PresidentsGroupWorkboard.as_view(),
         {'group_name': 'presidents'}, name='url_group_workboard'),
    path('vice-presidents-internal/', VicePresidentsInternalGroupWorkboard.as_view(),
         {'group_name': 'vice-presidents-internal'}, name='url_group_workboard'),
    path('treasurers/', TreasurersGroupWorkboard.as_view(),
         {'group_name': 'treasurers'}, name='url_group_workboard'),
    path('gadzarts/', GadzartsGroupWorkboard.as_view(),
         {'group_name': 'gadzarts'}, name='url_group_workboard'),
    path('<str:group_name>/', ShopGroupWorkboard.as_view(),
         name='url_group_workboard'),
    # MISC
    path('admin/', admin.site.urls),
    path('local/jsi18n/', jsi18n_catalog),
    ### APPS ###
    path('', include(finances_patterns)),
    path('', include(modules_patterns)),
    path('', include(notifications_patterns)),
    path('', include(settings_patterns)),
    path('', include(shops_patterns)),
    path('', include(stocks_patterns)),
    path('', include(users_patterns))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Cette ligne permet d'utiliser le dossier MEDIA en
# dev (en prod c'est automatique)
