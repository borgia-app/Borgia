from django.test import Client
from django.urls import reverse

from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from borgia.tests.utils import get_login_url_redirected
from finances.models import Cash, ExceptionnalMovement, Recharging, Transfert
from users.tests.tests_views import BaseFocusUserViewsTestCase


class BaseFinancesViewsTestCase(BaseBorgiaViewsTestCase):
    def setUp(self):
        super().setUp()
        cash = Cash.objects.create(sender=self.user2, amount=20)
        self.recharging1 = Recharging.objects.create(
            sender=self.user2, operator=self.user1, content_solution=cash)


class GeneralFinancesViewsTests(BaseFinancesViewsTestCase):
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
        self.assertRedirects(response_offline_user,
                             get_login_url_redirected(self.get_url()))


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


class RechargingListTests(GeneralFinancesViewsTests):
    url_view = 'url_recharging_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class RechargingRetrieveTests(BaseFinancesViewsTestCase):
    url_view = 'url_recharging_retrieve'

    def get_url(self, recharging_pk):
        return reverse(self.url_view, kwargs={'recharging_pk': recharging_pk})

    def test_get_allowed_user(self):
        response_client1 = self.client1.get(self.get_url(self.recharging1.pk))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_recharching(self):
        response_client1 = self.client1.get(self.get_url(5353))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_allowed_user(self):
        response_client2 = self.client2.get(self.get_url(self.recharging1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.recharging1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(
            self.get_url(self.recharging1.pk)))


class TransfertCreateTests(GeneralFinancesViewsTests):
    url_view = 'url_transfert_create'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class TransfertListTests(GeneralFinancesViewsTests):
    url_view = 'url_transfert_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class TransfertRetrieveTests(BaseFinancesViewsTestCase):
    url_view = 'url_transfert_retrieve'

    def get_url(self, transfert_pk):
        return reverse(self.url_view, kwargs={'transfert_pk': transfert_pk})

    def setUp(self):
        super().setUp()
        self.transfert1 = Transfert.objects.create(
            sender=self.user1, recipient=self.user2, amount=10)
        Transfert.objects.create(
            sender=self.user1, recipient=self.user2, amount=4)
        Transfert.objects.create(
            sender=self.user1, recipient=self.user2, amount=53)
        self.transfert4 = Transfert.objects.create(
            sender=self.user2, recipient=self.user1, amount=8)

    def test_allowed_user_get(self):
        response1_client1 = self.client1.get(self.get_url(self.transfert1.pk))
        response2_client1 = self.client1.get(self.get_url(self.transfert4.pk))
        self.assertEqual(response1_client1.status_code, 200)
        self.assertEqual(response2_client1.status_code, 200)

    def test_get_not_existing_recharching(self):
        response_client1 = self.client1.get(self.get_url(5353))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_allowed_user(self):
        response_client2 = self.client2.get(self.get_url(self.transfert1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def test_get_offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.transfert1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(
            self.get_url(self.transfert1.pk)))


class ExceptionnalMovementListTests(GeneralFinancesViewsTests):
    url_view = 'url_exceptionnalmovement_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ExceptionnalMovementRetrieveTests(BaseFinancesViewsTestCase):
    url_view = 'url_exceptionnalmovement_retrieve'

    def get_url(self, exceptionnalmovement_pk):
        return reverse(self.url_view, kwargs={'exceptionnalmovement_pk': exceptionnalmovement_pk})

    def setUp(self):
        super().setUp()
        self.movement1 = ExceptionnalMovement.objects.create(
            operator=self.user1, recipient=self.user2, amount=10)
        ExceptionnalMovement.objects.create(
            operator=self.user1, recipient=self.user2, amount=12)
        ExceptionnalMovement.objects.create(
            operator=self.user1, recipient=self.user2, amount=14)
        self.movement4 = ExceptionnalMovement.objects.create(
            operator=self.user2, recipient=self.user1, amount=9)

    def test_allowed_user_get(self):
        response1_client1 = self.client1.get(self.get_url(self.movement1.pk))
        response2_client1 = self.client1.get(self.get_url(self.movement4.pk))
        self.assertEqual(response1_client1.status_code, 200)
        self.assertEqual(response2_client1.status_code, 200)

    def test_not_existing_recharching_get(self):
        response_client1 = self.client1.get(self.get_url(5353))
        self.assertEqual(response_client1.status_code, 404)

    def test_not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url(self.movement1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection_get(self):
        response_offline_user = Client().get(self.get_url(self.movement1.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(
            self.get_url(self.movement1.pk)))
