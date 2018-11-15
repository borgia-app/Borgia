from django.contrib.auth.models import Group, Permission
from django.test import Client
from django.urls import reverse

from shops.models import Product, Shop
from shops.utils import DEFAULT_PERMISSIONS_CHIEFS
from users.tests.test_views import BaseUsersViewsTest


class BaseShopsViewsTest(BaseUsersViewsTest):
    def setUp(self):
        super().setUp()

        # SHOP CREATION
        self.shop1 = Shop.objects.create(
            name="shop1", description="The first shop ever", color="#F4FA58")
        chiefs = Group.objects.create(name='chiefs-' + self.shop1.name)
        chiefs.permissions.add()
        chiefs.save()

        # Add chiefs default permissions
        for codename in DEFAULT_PERMISSIONS_CHIEFS:
            perm = Permission.objects.get(codename=codename)
            chiefs.permissions.add(perm)

        self.user3.groups.add(chiefs)
        self.client3 = Client()
        self.client3.force_login(self.user3)

        self.product1 = Product.objects.create(
            name="skoll", shop=self.shop1)
        self.product2 = Product.objects.create(
            name="beer", unit='CL', shop=self.shop1)
        self.product3 = Product.objects.create(
            name="meat", unit='G', shop=self.shop1)


class ShopListViewTest(BaseShopsViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(
            reverse('url_shop_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_shop_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ShopCreateViewTest(BaseShopsViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(
            reverse('url_shop_create', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_shop_create', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ShopUpdateViewTest(BaseShopsViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(
            reverse('url_shop_update', kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_shop_update', kwargs={
            'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ShopCheckupViewTest(BaseShopsViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(
            reverse('url_shop_checkup', kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_shop_checkup', kwargs={
            'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductListViewTest(BaseShopsViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_product_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_chief(self):
        response_client3 = self.client3.get(
            reverse('url_product_list', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client3.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_product_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductCreateViewTest(BaseShopsViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_product_create', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_chief(self):
        response_client3 = self.client3.get(
            reverse('url_product_create', kwargs={'group_name': 'chiefs-shop1'}))
        self.assertEqual(response_client3.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_product_create', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductRetrieveViewTest(BaseShopsViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_product_retrieve', kwargs={'group_name': 'presidents', 'pk': '1'}))
        response_client2 = self.client1.get(
            reverse('url_product_retrieve', kwargs={'group_name': 'presidents', 'pk': '2'}))
        response_client3 = self.client1.get(
            reverse('url_product_retrieve', kwargs={'group_name': 'presidents', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_get_chief(self):
        response_client1 = self.client3.get(
            reverse('url_product_retrieve', kwargs={'group_name': 'chiefs-shop1', 'pk': '1'}))
        response_client2 = self.client3.get(
            reverse('url_product_retrieve', kwargs={'group_name': 'chiefs-shop1', 'pk': '2'}))
        response_client3 = self.client3.get(
            reverse('url_product_retrieve', kwargs={'group_name': 'chiefs-shop1', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_product_retrieve', kwargs={
            'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductUpdateViewTest(BaseShopsViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_product_update', kwargs={'group_name': 'presidents', 'pk': '1'}))
        response_client2 = self.client1.get(
            reverse('url_product_update', kwargs={'group_name': 'presidents', 'pk': '2'}))
        response_client3 = self.client1.get(
            reverse('url_product_update', kwargs={'group_name': 'presidents', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_get_chief(self):
        response_client1 = self.client3.get(
            reverse('url_product_update', kwargs={'group_name': 'chiefs-shop1', 'pk': '1'}))
        response_client2 = self.client3.get(
            reverse('url_product_update', kwargs={'group_name': 'chiefs-shop1', 'pk': '2'}))
        response_client3 = self.client3.get(
            reverse('url_product_update', kwargs={'group_name': 'chiefs-shop1', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_product_update', kwargs={
            'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductUpdatePriceViewTest(BaseShopsViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_product_update_price', kwargs={'group_name': 'presidents', 'pk': '1'}))
        response_client2 = self.client1.get(
            reverse('url_product_update_price', kwargs={'group_name': 'presidents', 'pk': '2'}))
        response_client3 = self.client1.get(
            reverse('url_product_update_price', kwargs={'group_name': 'presidents', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_get_chief(self):
        response_client1 = self.client3.get(
            reverse('url_product_update_price', kwargs={'group_name': 'chiefs-shop1', 'pk': '1'}))
        response_client2 = self.client3.get(
            reverse('url_product_update_price', kwargs={'group_name': 'chiefs-shop1', 'pk': '2'}))
        response_client3 = self.client3.get(
            reverse('url_product_update_price', kwargs={'group_name': 'chiefs-shop1', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_product_update_price', kwargs={
            'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductDeactivateViewTest(BaseShopsViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_product_deactivate', kwargs={'group_name': 'presidents', 'pk': '1'}))
        response_client2 = self.client1.get(
            reverse('url_product_deactivate', kwargs={'group_name': 'presidents', 'pk': '2'}))
        response_client3 = self.client1.get(
            reverse('url_product_deactivate', kwargs={'group_name': 'presidents', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_get_chief(self):
        response_client1 = self.client3.get(
            reverse('url_product_deactivate', kwargs={'group_name': 'chiefs-shop1', 'pk': '1'}))
        response_client2 = self.client3.get(
            reverse('url_product_deactivate', kwargs={'group_name': 'chiefs-shop1', 'pk': '2'}))
        response_client3 = self.client3.get(
            reverse('url_product_deactivate', kwargs={'group_name': 'chiefs-shop1', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_product_deactivate', kwargs={
            'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ProductRemoveViewTest(BaseShopsViewsTest):
    def test_get_president(self):
        response_client1 = self.client1.get(
            reverse('url_product_remove', kwargs={'group_name': 'presidents', 'pk': '1'}))
        response_client2 = self.client1.get(
            reverse('url_product_remove', kwargs={'group_name': 'presidents', 'pk': '2'}))
        response_client3 = self.client1.get(
            reverse('url_product_remove', kwargs={'group_name': 'presidents', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_get_chief(self):
        response_client1 = self.client3.get(
            reverse('url_product_remove', kwargs={'group_name': 'chiefs-shop1', 'pk': '1'}))
        response_client2 = self.client3.get(
            reverse('url_product_remove', kwargs={'group_name': 'chiefs-shop1', 'pk': '2'}))
        response_client3 = self.client3.get(
            reverse('url_product_remove', kwargs={'group_name': 'chiefs-shop1', 'pk': '3'}))
        self.assertEqual(response_client1.status_code, 200)
        self.assertEqual(response_client2.status_code, 200)
        self.assertEqual(response_client3.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_product_remove', kwargs={
            'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')
