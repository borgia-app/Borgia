from django.conf.urls import url

from modules.views import *

urlpatterns = [
    url(r'^(?P<shop_name>\w+)/(?P<url_module_name>\w+)/state/$',
        StandardModuleSetting.as_view(),
        kwargs={ 'fields': ['state'], 'title': 'Etat' },
        name='url_module_setting_state'),
    url(r'^(?P<shop_name>\w+)/(?P<url_module_name>\w+)/categories(?:/(?P<category_pk>\d+))?/$',
        CategoryModuleSetting.as_view(),
        name='url_shop_module_categories'),
    url(r'^(?P<shop_name>\w+)/(?P<url_module_name>\w+)/categories/create/$',
        CategoryCreate.as_view(),
        name='url_shop_module_create_category'),
    url(r'^(?P<shop_name>\w+)/(?P<url_module_name>\w+)/categories/delete/(?P<pk>\d+)/$',
        CategoryDelete.as_view(),
        name='url_shop_module_delete_category'),

    url(r'^(?P<shop_name>\w+)/self_sale/$',
        SelfSaleModuleView.as_view(),
        name='url_shop_module_self_sale')
]
