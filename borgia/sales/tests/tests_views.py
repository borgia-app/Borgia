import decimal

from django.test import Client
from django.urls import reverse

from borgia.tests.utils import get_login_url_redirected
from modules.tests.tests_views import BaseShopModuleViewsTest
from sales.models import Sale, SaleProduct


class BaseSalesViewsTest(BaseShopModuleViewsTest):
    def setUp(self):
        super().setUp()

        self.sale1 = Sale.objects.create(
            sender=self.user1,
            recipient=self.user3,
            operator=self.user3,
            shop=self.shop1,
            module=self.operatorsalemodule1
        )

        self.saleproduct1 = SaleProduct.objects.create(
            sale=self.sale1,
            product=self.product1,
            quantity=2,
            price=decimal.Decimal(1.23)
        )

        self.saleproduct2 = SaleProduct.objects.create(
            sale=self.sale1,
            product=self.product2,
            quantity=3,
            price=decimal.Decimal(4.56)
        )


class SaleListViewTests(BaseSalesViewsTest):
    url_view = 'url_sale_list'

    def get_url(self, shop_pk):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk})

    def test_as_president_get(self):
        response_client1 = self.client1.get(self.get_url(self.shop1.pk))
        self.assertEqual(response_client1.status_code, 200)

    def test_as_chief_get(self):
        response_client3 = self.client3.get(self.get_url(self.shop1.pk))
        self.assertEqual(response_client3.status_code, 200)

    def test_not_existing_shop_get(self):
        response_client1 = self.client1.get(self.get_url('5353'))
        self.assertEqual(response_client1.status_code, 404)

    def test_not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url(self.shop1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.shop1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(
            self.get_url(self.shop1.pk)))


class SaleRetrieveViewTests(BaseSalesViewsTest):
    url_view = 'url_sale_retrieve'

    def get_url(self, shop_pk, sale_pk):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk, 'sale_pk': sale_pk})

    def test_as_president_get(self):
        response_client1 = self.client1.get(
            self.get_url(self.shop1.pk, self.sale1.pk))
        self.assertEqual(response_client1.status_code, 200)

    def test_as_chief_get(self):
        response_client3 = self.client3.get(
            self.get_url(self.shop1.pk, self.sale1.pk))
        self.assertEqual(response_client3.status_code, 200)

    def test_not_existing_shop_get(self):
        response_client1 = self.client1.get(self.get_url(5353, self.sale1.pk))
        self.assertEqual(response_client1.status_code, 404)

    def test_not_existing_sale_get(self):
        response_client1 = self.client1.get(self.get_url(self.shop1.pk, 5353))
        self.assertEqual(response_client1.status_code, 404)

    def test_not_allowed_user_get(self):
        response_client2 = self.client2.get(
            self.get_url(self.shop1.pk, self.sale1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.shop1.pk, self.sale1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(
            self.get_url(self.shop1.pk, self.sale1.pk)))
