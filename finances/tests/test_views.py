from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.urls import reverse

from users.tests.test_views import BaseUsersViewsTest
from finances.models import Recharging, Transfert, Cash  # , Sale
# from shops.models import Shop
# from modules.models import ShopModule


class UserExceptionnalMovementCreateTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_exceptionnalmovement_create',
                                                    kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_user(self):
        response_client1 = self.client1.get(reverse('url_user_exceptionnalmovement_create',
                                                    kwargs={'group_name': 'presidents', 'user_pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_user_exceptionnalmovement_create',
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'user_pk': '2'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_user_exceptionnalmovement_create',
                                                    kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_user_exceptionnalmovement_create',
                                                    kwargs={'group_name': 'specials', 'user_pk': '2'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_exceptionnalmovement_create',
                                                     kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserSupplyMoneyTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_supplymoney',
                                                    kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_user(self):
        response_client1 = self.client1.get(reverse('url_user_supplymoney',
                                                    kwargs={'group_name': 'presidents', 'user_pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_user_supplymoney',
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'user_pk': '2'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_user_supplymoney',
                                                    kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_user_supplymoney',
                                                    kwargs={'group_name': 'specials', 'user_pk': '2'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_supplymoney',
                                                     kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class SaleListTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_sale_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_sale_list',
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_sale_list',
                                                    kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_sale_list',
                                                    kwargs={'group_name': 'specials'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_sale_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


# class SaleRetrieveTest(BaseFinancesViewsTest):
#     def setUp(self):
#         super().setUp()
#         shop = Shop.objects.create(name="shop", description="a beautiful shop", color="#F4FA58")
#         module = ShopModule.objects.create(shop=shop)
#         Sale.objects.create(sender=self.user2,
#                             recipient=self.user1,
#                             operator=self.user1,
#                             shop=shop,
#                             content_type_id=1,
#                             module_id=1)

#     def test_get_allowed_user(self):
#         response_client1 = self.client1.get(reverse('url_sale_retrieve',
#                                             kwargs={'group_name': 'presidents', 'pk': '1'}))
#         self.assertEqual(response_client1.status_code, 200)

#     def test_offline_user_redirection(self):
#         response_offline_user = Client().get(reverse('url_sale_retrieve',
#                                              kwargs={'group_name': 'presidents', 'pk': '1'}))
#         self.assertEqual(response_offline_user.status_code, 302)
#         self.assertRedirects(response_offline_user, '/auth/login/')


class RechargingListTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_recharging_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_recharging_list',
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_recharging_list',
                                                    kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_recharging_list',
                                                    kwargs={'group_name': 'specials'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_recharging_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class RechargingRetrieveTest(BaseUsersViewsTest):
    def setUp(self):
        super().setUp()
        cash = Cash.objects.create(sender=self.user2, recipient=self.user1, amount=20)
        Recharging.objects.create(sender=self.user2, operator=self.user1, payment_solution=cash)

    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_recharging_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_recharching(self):
        response_client1 = self.client1.get(reverse('url_recharging_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_recharging_retrieve',
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_recharging_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_recharging_retrieve',
                                                    kwargs={'group_name': 'specials', 'pk': '1'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_recharging_retrieve',
                                                     kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class TransfertListTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_transfert_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_transfert_list',
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_transfert_list',
                                                    kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_transfert_list',
                                                    kwargs={'group_name': 'specials'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_transfert_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class TransfertRetrieveTest(BaseUsersViewsTest):
    def setUp(self):
        super().setUp()
        Transfert.objects.create(sender=self.user1, recipient=self.user2, amount=10)

    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_transfert_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_recharching(self):
        response_client1 = self.client1.get(reverse('url_transfert_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_transfert_retrieve',
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_transfert_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_transfert_retrieve',
                                                    kwargs={'group_name': 'specials', 'pk': '1'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_transfert_retrieve',
                                                     kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')
