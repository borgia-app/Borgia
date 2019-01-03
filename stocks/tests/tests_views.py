from django.test import Client
from django.urls import reverse

from borgia.tests.utils import get_login_url_redirected
from shops.tests.tests_views import BaseShopsViewsTest
from stocks.models import (Inventory, InventoryProduct, StockEntry,
                           StockEntryProduct)


class BaseStocksViewsTest(BaseShopsViewsTest):
    def setUp(self):
        super().setUp()

        self.stockentry1 = StockEntry.objects.create(
            operator=self.user3, shop=self.shop1
        )
        self.stockentryproduct1 = StockEntryProduct.objects.create(
            stockentry=self.stockentry1, product=self.product1, quantity=53, price=53)
        self.stockentryproduct2 = StockEntryProduct.objects.create(
            stockentry=self.stockentry1, product=self.product2, quantity=5, price=10)
        self.stockentryproduct3 = StockEntryProduct.objects.create(
            stockentry=self.stockentry1, product=self.product3, quantity=1, price=9)

        self.inventory1 = Inventory.objects.create(
            operator=self.user3,
            shop=self.shop1
        )
        self.inventoryproduct1 = InventoryProduct.objects.create(
            inventory=self.inventory1, product=self.product1, quantity=53)
        self.inventoryproduct2 = InventoryProduct.objects.create(
            inventory=self.inventory1, product=self.product2, quantity=5)
        self.inventoryproduct3 = InventoryProduct.objects.create(
            inventory=self.inventory1, product=self.product3, quantity=1)


class BaseGeneralStocksViewsTest(BaseStocksViewsTest):
    url_view = None

    def get_url(self, shop_pk):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk})

    def president_get(self):
        response_client1 = self.client1.get(self.get_url(self.shop1.pk))
        self.assertEqual(response_client1.status_code, 200)

    def chief_get(self):
        response_client3 = self.client3.get(self.get_url(self.shop1.pk))
        self.assertEqual(response_client3.status_code, 200)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url(self.shop1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.shop1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url(self.shop1.pk)))


class StockEntryListViewTest(BaseGeneralStocksViewsTest):
    url_view = 'url_stockentry_list'

    def test_president_get(self):
        super().president_get()

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class StockEntryCreateViewTest(BaseGeneralStocksViewsTest):
    url_view = 'url_stockentry_create'

    def test_president_get(self):
        super().president_get()

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class StockEntryRetrieveViewTest(BaseStocksViewsTest):
    """
    Implement tests for views when focusing on a stockentry.
    """
    url_view = 'url_stockentry_retrieve'

    def get_url(self, shop_pk, stockentry_pk):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk, 'stockentry_pk': stockentry_pk})

    def as_president_get(self):
        response1_client1 = self.client1.get(self.get_url(self.shop1.pk, self.stockentry1.pk))
        self.assertEqual(response1_client1.status_code, 200)

    def as_chief_get(self):
        response1_client3 = self.client3.get(self.get_url(self.shop1.pk, self.stockentry1.pk))
        self.assertEqual(response1_client3.status_code, 200)

    def not_existing_stockentry_get(self):
        response_client1 = self.client1.get(self.get_url(self.shop1.pk, '5353'))
        self.assertEqual(response_client1.status_code, 404)

    def not_existing_shop_get(self):
        response_client1 = self.client1.get(self.get_url('5353', self.stockentry1.pk))
        self.assertEqual(response_client1.status_code, 404)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url(self.shop1.pk, self.stockentry1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.shop1.pk, self.stockentry1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url(self.shop1.pk, self.stockentry1.pk)))


class InventoryListViewTest(BaseGeneralStocksViewsTest):
    url_view = 'url_inventory_list'

    def test_president_get(self):
        super().president_get()

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class InventoryCreateViewTest(BaseGeneralStocksViewsTest):
    url_view = 'url_inventory_create'

    def test_president_get(self):
        super().president_get()

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class InventoryRetrieveViewTest(BaseStocksViewsTest):
    """
    Implement tests for views when focusing on an inventory.
    """
    url_view = 'url_inventory_retrieve'

    def get_url(self, shop_pk, inventory_pk):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk, 'inventory_pk': inventory_pk})

    def as_president_get(self):
        response1_client1 = self.client1.get(self.get_url(self.shop1.pk, self.inventory1.pk))
        self.assertEqual(response1_client1.status_code, 200)

    def as_chief_get(self):
        response1_client3 = self.client3.get(self.get_url(self.shop1.pk, self.inventory1.pk))
        self.assertEqual(response1_client3.status_code, 200)

    def not_existing_stockentry_get(self):
        response_client1 = self.client1.get(self.get_url(self.shop1.pk, '5353'))
        self.assertEqual(response_client1.status_code, 404)

    def not_existing_shop_get(self):
        response_client1 = self.client1.get(self.get_url('5353', self.inventory1.pk))
        self.assertEqual(response_client1.status_code, 404)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url(self.shop1.pk, self.inventory1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.shop1.pk, self.inventory1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url(self.shop1.pk, self.inventory1.pk)))
