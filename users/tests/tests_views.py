from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import NoReverseMatch, reverse

from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from borgia.utils import get_members_group
from users.models import User


class UsersViewNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named users URLs should be reversible"
        expected_named_urls = [
            ('url_user_list', [], {}),
            ('url_user_create', [], {}),
            ('url_user_retrieve', [], {'pk': 53}),
            ('url_user_update', [], {'pk': 53}),
            ('url_user_deactivate', [], {'pk': 53}),
            ('url_user_self_update', [], {}),
            ('url_group_update', [], {'pk': 53}),
            ('url_ajax_username_from_username_part', [], {}),
            ('url_balance_from_username', [], {}),
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail("Reversal of url named '%s' failed with NoReverseMatch" % name)


class BaseGeneralUserViewsTestCase(BaseBorgiaViewsTestCase):
    url_view = None

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view))
        self.assertEqual(response_client1.status_code, 200)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserListViewTestCase(BaseGeneralUserViewsTestCase):
    url_view = 'url_user_list'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class UserCreateViewTestCase(BaseGeneralUserViewsTestCase):
    url_view = 'url_user_create'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()

    def test_create_internal_member(self):
        response_creation = self.client1.post(
            reverse(self.url_view),
            {'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'not_a_real_email@email.com',
            'family': '53',
            'year': 2015,
            'campus': 'ME',
            'username': '53Me215',
            'password': 'password'})
        
        self.assertEqual(response_creation.status_code, 302)
        self.assertTrue(Client().login(username='53Me215', password='password'))
        user = User.objects.get(username='53Me215')
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(user.groups.first(), get_members_group())

    def test_create_external_member(self):
        response_creation = self.client1.post(
            reverse(self.url_view),
            {'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'not_a_real_email2@email.com',
            'year': 2015,
            'username': 'External',
            'is_external_member': True,
            'password': 'password'})
        
        self.assertEqual(response_creation.status_code, 302)
        self.assertTrue(Client().login(username='External', password='password'))
        user = User.objects.get(username='External')
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(user.groups.first(), get_members_group(externals=True))


class BaseFocusUserViewsTestCase(BaseBorgiaViewsTestCase):
    url_view = None

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def not_existing_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view, kwargs={'pk': '3'}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view, kwargs={'pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')

class UserRetrieveViewTestCase(BaseFocusUserViewsTestCase):
    url_view = 'url_user_retrieve'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class UserUpdateViewTestCase(BaseFocusUserViewsTestCase):
    url_view = 'url_user_update'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class UserDeactivateViewTestCase(BaseFocusUserViewsTestCase):
    url_view = 'url_user_deactivate'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_self_deactivate_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view, kwargs={'pk': str(self.user2.pk)}))
        self.assertEqual(response_client2.status_code, 200)

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class UserSelfUpdateViewTestCase(BaseBorgiaViewsTestCase):
    url_view = 'url_user_self_update'


    def test_allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view))
        self.assertEqual(response_client1.status_code, 200)

    def test_other_allowed_user_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view))
        self.assertEqual(response_client2.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ManageGroupViewTestCase(BaseBorgiaViewsTestCase):
    url_view = 'url_user_deactivate'

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def not_existing_focus_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view, kwargs={'pk': '535353'}))
        self.assertEqual(response_client1.status_code, 404)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view, kwargs={'pk': '1'}))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view, kwargs={'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')
