#-*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from settings_data.views import *


urlpatterns = [
    # Models
    url(r'^setting/$', permission_required('settings_data.change_setting')
    (ListSettingView.as_view()), name='url_list_setting'),
    url(r'^setting/update/(?P<pk>\d+)/$', permission_required('settings_data.change_setting')
    (UpdateSettingView.as_view()), name='url_update_setting'),
]