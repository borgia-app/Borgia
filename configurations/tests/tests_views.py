from django.test import Client
from django.urls import reverse

from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from borgia.tests.utils import get_login_url_redirected


class BaseConfigurationsViewsTest(BaseBorgiaViewsTestCase):
    url_view = None

    def get_url(self):
        return reverse(self.url_view)

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            self.get_url())
        self.assertEqual(response_client1.status_code, 200)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url())
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url())
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url()))


class GlobalConfigTest(BaseConfigurationsViewsTest):
    url_view = 'url_index_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class CenterConfigTest(BaseConfigurationsViewsTest):
    url_view = 'url_center_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class PriceConfigTest(BaseConfigurationsViewsTest):
    url_view = 'url_price_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class LydiaConfigTest(BaseConfigurationsViewsTest):
    url_view = 'url_lydia_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()

class BalanceConfigTest(BaseConfigurationsViewsTest):
    url_view = 'url_balance_config'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()
