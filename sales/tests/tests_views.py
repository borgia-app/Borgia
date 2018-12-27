#-*- coding: utf-8 -*-
from django.test import Client
from django.urls import reverse

from shops.tests.tests_views import BaseFocusShopViewsTest


class SaleListTests(BaseFocusShopViewsTest):
    url_view = 'url_sale_list'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_chief_get(self):
        super().as_chief_get()

    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()
