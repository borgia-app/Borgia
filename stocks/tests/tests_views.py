from django.test import Client
from django.urls import reverse

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


class StockEntryListViewTest(BaseStocksViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_stock_entry_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_chief(self):
        response_client3 = self.client3.get(
            reverse('url_stock_entry_list', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client3.status_code, 200)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_stock_entry_list',
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client2 = self.client2.get(reverse('url_stock_entry_list',
                                                    kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_stock_entry_list',
                                                    kwargs={'group_name': 'externals'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_stock_entry_list', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class StockEntryCreateViewTest(BaseStocksViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_stock_entry_create', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_chief(self):
        response_client3 = self.client3.get(
            reverse('url_stock_entry_create', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client3.status_code, 200)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_stock_entry_create',
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client2 = self.client2.get(reverse('url_stock_entry_create',
                                                    kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_stock_entry_create',
                                                    kwargs={'group_name': 'externals'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_stock_entry_create', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class StockEntryRetrieveViewTest(BaseStocksViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(reverse('url_stock_entry_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': str(self.stockentry1.pk)}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_chief(self):
        response_client3 = self.client3.get(
            reverse('url_stock_entry_retrieve', kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.stockentry1.pk)}))
        self.assertEqual(response_client3.status_code, 200)

    def test_get_not_existing_inventory(self):
        response_client3 = self.client3.get(reverse('url_stock_entry_retrieve',
                                                    kwargs={'group_name': 'chiefs-shop1', 'pk': '535353'}))
        self.assertEqual(response_client3.status_code, 404)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_stock_entry_retrieve',
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'pk': str(self.stockentry1.pk)}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client2 = self.client2.get(reverse('url_stock_entry_retrieve',
                                                    kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.stockentry1.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_stock_entry_retrieve',
                                                    kwargs={'group_name': 'externals', 'pk': str(self.stockentry1.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_stock_entry_retrieve', kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.stockentry1.pk)}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class InventoryListViewTest(BaseStocksViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_inventory_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_chief(self):
        response_client3 = self.client3.get(
            reverse('url_inventory_list', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client3.status_code, 200)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_inventory_list',
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client2 = self.client2.get(reverse('url_inventory_list',
                                                    kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_inventory_list',
                                                    kwargs={'group_name': 'externals'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_inventory_list', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class InventoryCreateViewTest(BaseStocksViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_inventory_create', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_chief(self):
        response_client3 = self.client3.get(
            reverse('url_inventory_create', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client3.status_code, 200)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_inventory_create',
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client2 = self.client2.get(reverse('url_inventory_create',
                                                    kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_inventory_create',
                                                    kwargs={'group_name': 'externals'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_inventory_create', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class InventoryRetrieveViewTest(BaseStocksViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(reverse('url_inventory_retrieve', kwargs={
            'group_name': 'presidents', 'pk': str(self.inventory1.pk)}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_chief(self):
        response_client3 = self.client3.get(
            reverse('url_inventory_retrieve', kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.inventory1.pk)}))
        self.assertEqual(response_client3.status_code, 200)

    def test_get_not_existing_inventory(self):
        response_client3 = self.client3.get(reverse('url_inventory_retrieve',
                                                    kwargs={'group_name': 'chiefs-shop1', 'pk': '535353'}))
        self.assertEqual(response_client3.status_code, 404)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_inventory_retrieve',
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'pk': str(self.inventory1.pk)}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client2 = self.client2.get(reverse('url_inventory_retrieve',
                                                    kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.inventory1.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_inventory_retrieve',
                                                    kwargs={'group_name': 'externals', 'pk': str(self.inventory1.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_inventory_retrieve', kwargs={'group_name': 'chiefs-shop1', 'pk': str(self.inventory1.pk)}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')
