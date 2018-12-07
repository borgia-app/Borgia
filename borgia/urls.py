from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import (password_change, password_change_done,
                                       password_reset, password_reset_complete,
                                       password_reset_confirm,
                                       password_reset_done)
from django.urls import include, path

from borgia.views import (GadzartsGroupWorkboard, Login, Logout,
                          PresidentsGroupWorkboard, ShopGroupWorkboard,
                          TreasurersGroupWorkboard,
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
    # WORKBOARDS
    path('presidents/', PresidentsGroupWorkboard.as_view(),
         {'group_name': 'presidents'}, name='url_group_workboard'),
    path('vice-presidents-internal/', VicePresidentsInternalGroupWorkboard.as_view(),
         {'group_name': 'vice-presidents-internal'}, name='url_group_workboard'),
    path('treasurers/', TreasurersGroupWorkboard.as_view(), {'group_name': 'treasurers'}, name='url_group_workboard'),
    path('gadzarts/', GadzartsGroupWorkboard.as_view(), {'group_name': 'gadzarts'}, name='url_group_workboard'),
    path('<str:group_name>/', ShopGroupWorkboard.as_view(), name='url_group_workboard'),
    # AUTHENTIFICATIONS
    path('', Login.as_view()),
    path('auth/', include([
        path('logout/', Logout.as_view(), name='url_logout'),
        path('login/', Login.as_view(), {'save_login_url': False}, name='url_login'),
        path('gadzarts/<str:shop_name>', Login.as_view(), {'save_login_url': True, 'gadzarts': True}, name='url_login_direct_module_selfsale'),
        path('password_reset/', password_reset, name='reset_password_reset1'),
        path('password_reset/done/', password_reset_done,
             name='password_reset_done'),
        path('<str:uidb64>/<str:token>/', password_reset_confirm,
             name='password_reset_confirm'),
        path('done/', password_reset_complete, name='password_reset_complete'),
        path('password_change/', password_change, {'post_change_redirect': password_change_done}, name='password_change'),
        path('password_change_done/', password_change_done,
             name='password_change_done'),
        path('<str:shop_name>/', Login.as_view(), {'save_login_url': True, 'gadzarts': False}, name='url_login_direct_module_operatorsale')
    ])),
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
