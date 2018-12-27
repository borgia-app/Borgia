from django.test import Client
from django.urls import reverse

from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from finances.models import Cash, Recharging, Transfert, ExceptionnalMovement
from shops.tests.tests_views import BaseFocusShopViewsTest
from users.tests.tests_views import BaseFocusUserViewsTestCase

class BaseFinancesViewsTestCase(BaseBorgiaViewsTestCase):
    url_view = None

    def get_url(self):
        return reverse(self.url_view)

    def allowed_user_get(self):
        response_client1 = self.client1.get(self.get_url())
        self.assertEqual(response_client1.status_code, 200)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url())
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url())
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserExceptionnalMovementCreateTests(BaseFocusUserViewsTestCase):
    url_view = 'url_user_exceptionnalmovement_create'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class RechargingCreateTests(BaseFocusUserViewsTestCase):
    url_view = 'url_recharging_create'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


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


class RechargingListTests(BaseFinancesViewsTestCase):
    url_view = 'url_recharging_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class RechargingRetrieveTests(BaseBorgiaViewsTestCase):
    url_view = 'url_recharging_retrieve'

    def get_url(self, recharging_pk):
        return reverse(self.url_view, kwargs={'recharging_pk': recharging_pk})

    def setUp(self):
        super().setUp()
        cash = Cash.objects.create(sender=self.user2, recipient=self.user1, amount=20)
        Recharging.objects.create(sender=self.user2, operator=self.user1, payment_solution=cash)

    def test_get_allowed_user(self):
        response_client1 = self.client1.get(self.get_url(1))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_recharching(self):
        response_client1 = self.client1.get(self.get_url(5353))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_allowed_user(self):
        response_client2 = self.client2.get(self.get_url(1))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(1))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class TransfertListTests(BaseFinancesViewsTestCase):
    url_view = 'url_transfert_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class TransfertRetrieveTests(BaseBorgiaViewsTestCase):
    url_view = 'url_transfert_retrieve'

    def get_url(self, transfert_pk):
        return reverse(self.url_view, kwargs={'transfert_pk': transfert_pk})

    def setUp(self):
        super().setUp()
        Transfert.objects.create(sender=self.user1, recipient=self.user2, amount=10)

    def test_get_allowed_user(self):
        response_client1 = self.client1.get(self.get_url(1))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_recharching(self):
        response_client1 = self.client1.get(self.get_url(5353))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_allowed_user(self):
        response_client2 = self.client2.get(self.get_url(1))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(1))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ExceptionnalMovementListTests(BaseFinancesViewsTestCase):
    url_view = 'url_exceptionnalmovement_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ExceptionnalMovementRetrieveTests(BaseBorgiaViewsTestCase):
    url_view = 'url_exceptionnalmovement_retrieve'

    def get_url(self, exceptionnalmovement_pk):
        return reverse(self.url_view, kwargs={'exceptionnalmovement_pk': exceptionnalmovement_pk})

    def setUp(self):
        super().setUp()
        ExceptionnalMovement.objects.create(operator=self.user1, recipient=self.user2, amount=10)

    def test_get_allowed_user(self):
        response_client1 = self.client1.get(self.get_url(1))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_recharching(self):
        response_client1 = self.client1.get(self.get_url(5353))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_allowed_user(self):
        response_client2 = self.client2.get(self.get_url(1))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(1))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')
