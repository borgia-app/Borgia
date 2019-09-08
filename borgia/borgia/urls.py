from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (LogoutView, PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import include, path

from borgia.views import ManagersWorkboard, MembersWorkboard, ModulesLoginView
from configurations.urls import configurations_patterns
from events.urls import events_patterns
from finances.urls import finances_patterns
from modules.urls import modules_patterns
from sales.urls import sales_patterns
from shops.urls import shops_patterns
from stocks.urls import stocks_patterns
from users.urls import users_patterns


urlpatterns = [
    # AUTHENTIFICATIONS
    path('', ModulesLoginView.as_view(), name='url_login'),
    path('auth/', include([
        path('login/', ModulesLoginView.as_view(), name='url_login'),
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
    path('members/', MembersWorkboard.as_view(), name='url_members_workboard'),
    path('managers/', ManagersWorkboard.as_view(),
         name='url_managers_workboard'),

    ### APPS ###
    path('', include(configurations_patterns)),
    path('', include(events_patterns)),
    path('', include(finances_patterns)),
    path('', include(modules_patterns)),
    path('', include(sales_patterns)),
    path('', include(shops_patterns)),
    path('', include(stocks_patterns)),
    path('', include(users_patterns))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Cette ligne permet d'utiliser le dossier MEDIA en
# dev (en prod c'est automatique)
