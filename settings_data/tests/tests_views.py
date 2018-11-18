from django.test import Client
from django.urls import reverse

from users.tests.tests_views import BaseUsersViewsTest


class BaseSettingsViewsTest(BaseUsersViewsTest):
    url_view = None

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def not_existing_group_get(self):
        response_client1 = self.client1.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_in_group_user_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client2.status_code, 403)

    def not_allowed_group_get(self):
        response_client2 = self.client2.get(reverse(self.url_view,
                                                    kwargs={'group_name': 'specials'}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')

class GlobalConfigTest(BaseSettingsViewsTest):
    url_view = 'url_global_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()

class CenterConfigTest(BaseSettingsViewsTest):
    url_view = 'url_center_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()

class PriceConfigTest(BaseSettingsViewsTest):
    url_view = 'url_price_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()

class LydiaConfigTest(BaseSettingsViewsTest):
    url_view = 'url_lydia_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()

class BalanceConfigTest(BaseSettingsViewsTest):
    url_view = 'url_balance_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()
