from django.test import Client
from django.urls import reverse

from borgia.tests.utils import get_login_url_redirected
from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from borgia.utils import get_members_group
from users.models import User


class BaseGeneralUserViewsTestCase(BaseBorgiaViewsTestCase):
    url_view = None

    def get_url(self):
        return reverse(self.url_view)

    def allowed_user_get(self):
        response_client1 = self.client1.get(
            self.get_url())
        self.assertEqual(response_client1.status_code, 200)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(
            self.get_url())
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url()))


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
        self.assertEqual(user.groups.first(), get_members_group(is_externals=True))


class BaseFocusUserViewsTestCase(BaseBorgiaViewsTestCase):
    url_view = None

    def get_url(self, user_pk):
        return reverse(self.url_view, kwargs={'user_pk': user_pk})

    def allowed_user_get(self):
        response_client1 = self.client1.get(self.get_url(self.user2.pk))
        self.assertEqual(response_client1.status_code, 200)

    def not_existing_user_get(self):
        response_client1 = self.client1.get(self.get_url(5353))
        self.assertEqual(response_client1.status_code, 404)

    def not_allowed_user_get(self):
        response_client2 = self.client2.get(self.get_url(self.user1.pk))
        self.assertEqual(response_client2.status_code, 403)

    def offline_user_redirection(self):
        response_offline_user = Client().get(self.get_url(self.user2.pk))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url(self.user2.pk)))

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
    
    def test_allowed_selfupdate_get(self):
        response_client1 = self.client1.get(
            self.get_url(self.user1.pk))
        self.assertEqual(response_client1.status_code, 200)

    def test_allowed_selfupdate2_get(self):
        response_client2 = self.client2.get(
            self.get_url(self.user2.pk))
        self.assertEqual(response_client2.status_code, 200)


class UserDeactivateViewTestCase(BaseFocusUserViewsTestCase):
    url_view = 'url_user_deactivate'

    def test_allowed_user_get(self):
        super().allowed_user_get()

    def test_not_existing_user_get(self):
        super().not_existing_user_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_self_deactivate_get(self):
        response_client2 = self.client2.get(self.get_url(self.user2.pk))
        self.assertEqual(response_client2.status_code, 200)

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class UpdateGroupViewTestCase(BaseBorgiaViewsTestCase):
    url_view = 'url_group_update'

    def get_url(self, group_pk):
        return reverse(self.url_view, kwargs={'group_pk': group_pk})

    def test_allowed_user_get(self):
        for group_pk in range(1, 4):
            response_client1 = self.client1.get(
                self.get_url(group_pk))
            self.assertEqual(response_client1.status_code, 200)

    def test_not_existing_focus_get(self):
        response_client1 = self.client1.get(
            self.get_url(5353))
        self.assertEqual(response_client1.status_code, 404)

    def test_not_allowed_user_get(self):
        response_client2 = self.client2.get(
            self.get_url(1))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(
            self.get_url(1))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url(1)))
