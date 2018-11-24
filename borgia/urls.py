from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (LogoutView, PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import include, path

from borgia.views import (MembersGroupWorkboard, ModulesLoginView,
                          PresidentsGroupWorkboard, ShopGroupWorkboard,
                          TreasurersGroupWorkboard,
                          VicePresidentsInternalGroupWorkboard, handler403,
                          handler404, handler500)
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
    path('', ModulesLoginView.as_view(), name='url_login'),
    path('auth/', include([
        path('login/', ModulesLoginView.as_view()),
        path('logout/', LogoutView.as_view(), name='url_logout'),

        path('password_change/', PasswordChangeView.as_view(),
             name='password_change'),
        path('password_change/done/', PasswordChangeDoneView.as_view(),
             name='password_change_done'),

        path('password_reset/', PasswordResetView.as_view(),
             name='password_reset'),
        path('password_reset/done/', PasswordResetDoneView.as_view(),
             name='password_reset_done'),
        path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
             name='password_reset_confirm'),
        path('reset/done/', PasswordResetCompleteView.as_view(),
             name='password_reset_complete'),
    ])),
    # WORKBOARDS
    path('presidents/', PresidentsGroupWorkboard.as_view(),
         {'group_name': 'presidents'}, name='url_group_workboard'),
    path('vice_presidents/', VicePresidentsInternalGroupWorkboard.as_view(),
         {'group_name': 'vice_presidents'}, name='url_group_workboard'),
    path('treasurers/', TreasurersGroupWorkboard.as_view(),
         {'group_name': 'treasurers'}, name='url_group_workboard'),
    path('members/', MembersGroupWorkboard.as_view(),
         {'group_name': 'members'}, name='url_group_workboard'),
    path('<str:group_name>/', ShopGroupWorkboard.as_view(),
         name='url_group_workboard'),
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
