from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import reverse

from borgia.tests.tests_views import BaseBorgiaViewsTestCase


class BaseGeneralUserViewsTestCase(BaseBorgiaViewsTestCase):
    url_view = None

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def not_existing_group_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_in_group_user_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client2.status_code, 403)

    def not_allowed_group_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view, kwargs={'group_name': 'externals'}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view, kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserListViewTestCase(BaseGeneralUserViewsTestCase):
    url_view = 'url_user_list'

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


class UserCreateViewTestCase(BaseGeneralUserViewsTestCase):
    url_view = 'url_user_create'

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


class BaseFocusUserViewsTestCase(BaseBorgiaViewsTestCase):
    url_view = None

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def not_existing_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_existing_group_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'group_that_does_not_exist', 'pk': '2'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_in_group_user_get(self):
        response_client3 = self.client3.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_client3.status_code, 403)

    def not_allowed_group_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view, kwargs={'group_name': 'externals', 'pk': '2'}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')

class UserRetrieveViewTestCase(BaseFocusUserViewsTestCase):
    url_view = 'url_user_retrieve'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class UserUpdateViewTestCase(BaseFocusUserViewsTestCase):
    url_view = 'url_user_update'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class UserDeactivateViewTestCase(BaseFocusUserViewsTestCase):
    url_view = 'url_user_deactivate'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_existing_group_get(self):
        super().not_existing_group_get()

    def test_not_in_group_user_get(self):
        super().not_in_group_user_get()

    def test_not_allowed_group_get(self):
        super().not_allowed_group_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class UserSelfDeactivateViewTestCase(BaseBorgiaViewsTestCase):
    def test_get_allowed_user(self):
        response_client = self.client1.get(reverse('url_self_deactivate', kwargs={
                                           'group_name': 'gadzarts', 'pk': str(self.user1.pk)}))
        self.assertEqual(response_client.status_code, 200)

    def test_get_not_existing_user(self):
        response_client1 = self.client1.get(reverse('url_user_deactivate',
                                                    kwargs={'group_name': 'gadzarts', 'pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_on_another_user(self):
        response_client1 = self.client1.get(reverse('url_user_deactivate',
                                                    kwargs={'group_name': 'gadzarts', 'pk': str(self.user2.pk)}))
        self.assertEqual(response_client1.status_code, 403)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_user_deactivate',
                                                    kwargs={'group_name': 'group_that_does_not_exist', 'pk': str(self.user1.pk)}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_user_deactivate',
                                                    kwargs={'group_name': 'gadzarts', 'pk': str(self.user3.pk)}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_user_deactivate',
                                                    kwargs={'group_name': 'externals', 'pk': str(self.user2.pk)}))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_self_deactivate', kwargs={
            'group_name': 'gadzarts', 'pk': str(self.user1.pk)}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserSelfUpdateViewTestCase(BaseBorgiaViewsTestCase):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(
            reverse('url_user_self_update', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_get_not_existing_group(self):
        response_client1 = self.client1.get(reverse('url_user_self_update',
                                                    kwargs={'group_name': 'group_that_does_not_exist'}))
        self.assertEqual(response_client1.status_code, 404)

    def test_get_not_in_group_user(self):
        response_client3 = self.client3.get(reverse('url_user_self_update',
                                                    kwargs={'group_name': 'gadzarts'}))
        self.assertEqual(response_client3.status_code, 403)

    def test_get_not_allowed_group(self):
        response_client2 = self.client2.get(reverse('url_user_self_update',
                                                    kwargs={'group_name': 'externals'}))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse('url_user_self_update', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ManageGroupViewTestCase(BaseBorgiaViewsTestCase):
    url_view = 'url_user_deactivate'

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def not_existing_focus_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_existing_group_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'group_name': 'group_that_does_not_exist', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_in_group_user_get(self):
        response_client3 = self.client3.get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client3.status_code, 403)

    def not_allowed_group_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view, kwargs={'group_name': 'externals', 'pk': '1'}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view, kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')