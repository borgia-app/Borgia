from django.contrib.auth.models import Group, Permission
# from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.urls import reverse

from users.models import User
from finances.models import Recharging, Transfert, Cash  # , Sale
# from shops.models import Shop
# from modules.models import ShopModule


class BaseFinancesViewsTest(TestCase):
    def setUp(self):
        members_group = Group.objects.create(name='gadzarts')
        presidents_group = Group.objects.create(name='presidents')
        presidents_group.permissions.set(Permission.objects.all())
        # Group specials NEED to be created (else raises errors) :
        specials_group = Group.objects.create(name='specials')
        specials_group.permissions.set([])

        self.user1 = User.objects.create(username='user1', balance=100)
        self.user1.groups.add(members_group)
        self.user1.groups.add(presidents_group)
        self.user2 = User.objects.create(username='user2', balance=100)
        self.user2.groups.add(specials_group)
        self.user3 = User.objects.create(username='user3')
        self.client1 = Client()
        self.client1.force_login(self.user1)        
        self.client2 = Client()
        self.client2.force_login(self.user2)


class UserExceptionnalMovementCreateTest(BaseFinancesViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_exceptionnalmovement_create',
                                                    kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_exceptionnalmovement_create',
                                                     kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserSupplyMoneyTest(BaseFinancesViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_supplymoney',
                                                    kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_supplymoney',
                                                     kwargs={'group_name': 'presidents', 'user_pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class SaleListTest(BaseFinancesViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_sale_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
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


class RechargingListTest(BaseFinancesViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_recharging_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_recharging_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class RechargingRetrieveTest(BaseFinancesViewsTest):
    def setUp(self):
        super().setUp()
        cash = Cash.objects.create(sender=self.user2, recipient=self.user1, amount=20)
        Recharging.objects.create(sender=self.user2, operator=self.user1, payment_solution=cash)

    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_recharging_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_recharging_retrieve',
                                                     kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class TransfertListTest(BaseFinancesViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_transfert_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_transfert_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class TransfertRetrieveTest(BaseFinancesViewsTest):
    def setUp(self):
        super().setUp()
        Transfert.objects.create(sender=self.user1, recipient=self.user2, amount=10)

    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_transfert_retrieve',
                                                    kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_transfert_retrieve',
                                                     kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')
