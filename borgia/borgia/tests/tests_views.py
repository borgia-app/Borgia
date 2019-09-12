from django.contrib.auth import get_user
from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import NoReverseMatch, reverse

from borgia.settings import LOGIN_REDIRECT_URL, LOGIN_URL
from borgia.tests.utils import get_login_url_redirected
from borgia.utils import EXTERNALS_GROUP_NAME, INTERNALS_GROUP_NAME, PRESIDENTS_GROUP_NAME
from users.models import User


class BaseBorgiaViewsTestCase(TestCase):
    fixtures = ['initial', 'tests_data']

    def setUp(self):
        members_group = Group.objects.get(name=INTERNALS_GROUP_NAME)
        externals_group = Group.objects.get(name=EXTERNALS_GROUP_NAME)
        presidents_group = Group.objects.get(name=PRESIDENTS_GROUP_NAME)
        presidents_group.permissions.set(Permission.objects.all())
        # Group externals NEED to be created (else raises errors) :

        self.user1 = User.objects.create(username='user1', balance=53)
        self.user1.groups.add(members_group)
        self.user1.groups.add(presidents_group)
        self.user1.save()
        self.user2 = User.objects.create(username='user2', balance=144)
        self.user2.groups.add(externals_group)
        self.user2.save()
        self.user3 = User.objects.create(username='user3')
        self.client1 = Client()
        self.client1.force_login(self.user1)
        self.client2 = Client()
        self.client2.force_login(self.user2)
        self.client3 = Client()
        self.client3.force_login(self.user3)


class AuthViewNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named URLs should be reversible"
        expected_named_urls = [
            ('url_login', [], {}),
            ('url_logout', [], {}),
            ('password_change', [], {}),
            ('password_change_done', [], {}),
            ('password_reset', [], {}),
            ('password_reset_done', [], {}),
            ('password_reset_confirm', [], {
                'uidb64': 'aaaaaaa',
                'token': '1111-aaaaa',
            }),
            ('password_reset_complete', [], {}),
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail("Reversal of url named '%s' failed with NoReverseMatch" % name)


class BaseAuthViewsTestCase(TestCase):
    fixtures = ['initial', 'tests_data']
    url_view = None

    def setUp(self):
        self.user = User.objects.create(username='user')
        self.user.set_password('yaquela215quipine')
        self.user.save()

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url()))

    def get_url(self):
        return reverse(self.url_view)


class LoginViewTests(BaseAuthViewsTestCase):
    url_view = 'url_login'
    template_name = 'registration/login.html'

    def test_get(self):
        response = Client().get(reverse(self.url_view))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_alternative_get(self):
        response = Client().get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_login(self):
        client = Client()
        response = client.post(
            reverse(self.url_view),
            {'username': 'user', 'password': 'yaquela215quipine'})

        user_logged = get_user(client)
        self.assertTrue(user_logged.is_authenticated)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_wrong_credentials(self):
        client = Client()
        response = client.post(
            reverse(self.url_view),
            {'username': 'user', 'password': 'wrongpassword'})

        user_logged = get_user(client)
        self.assertFalse(user_logged.is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)


class LogoutViewTests(BaseAuthViewsTestCase):
    url_view = 'url_logout'

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.force_login(self.user)

    def test_logout(self):
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        response = self.client.get(reverse(self.url_view))

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.assertEqual(response.status_code, 302)

    def test_redirection(self):
        response = Client().get(reverse(self.url_view))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, LOGIN_URL)

    def get_url(self):
        return reverse(self.url_view)


class PasswordChangeViewTests(BaseAuthViewsTestCase):
    url_view = 'password_change'
    template_name = 'registration/password_change_form.html'

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.force_login(self.user)

    def test_logged_get(self):
        response = self.client.get(reverse(self.url_view))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_post(self):
        response = self.client.post(
            reverse(self.url_view),
            {'username': 'user',
             'old_password': 'yaquela215quipine',
             'new_password1': 'new_password',
             'new_password2': 'new_password'})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_change_done'))

        client2 = Client()
        client2.login(username='user', password='yaquela215quipine')
        user_wrong_credentials = get_user(client2)
        self.assertFalse(user_wrong_credentials.is_authenticated)
        client3 = Client()
        client3.login(username='user', password='new_password')
        user_logged = get_user(client3)
        self.assertTrue(user_logged.is_authenticated)

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class PasswordChangeDoneViewTests(BaseAuthViewsTestCase):
    url_view = 'password_change_done'
    template_name = 'registration/password_change_done.html'

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(reverse(self.url_view))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class PasswordResetViewTests(BaseBorgiaViewsTestCase):
    url_view = 'password_reset'
    template_name = 'registration/password_reset_form.html'

    def test_get(self):
        response = Client().get(reverse(self.url_view))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_reset_valid(self):
        response = Client().post(
            reverse(self.url_view),
            {'email': 'passwordreset@test.case'})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_done'))


class PasswordResetDoneViewTests(BaseBorgiaViewsTestCase):
    url_view = 'password_reset_done'
    template_name = 'registration/password_reset_done.html'

    def test_get(self):
        response = Client().get(reverse(self.url_view))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)


class BaseWorkboardsTestCase(BaseBorgiaViewsTestCase):
    """
    Base for workboards test cases
    """
    url_view = None

    def as_president_get(self):
        response_client1 = self.client1.get(
            reverse(self.url_view))
        self.assertEqual(response_client1.status_code, 200)

    def offline_user_redirection(self):
        response_offline_user = Client().get(
            reverse(self.url_view))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, get_login_url_redirected(self.get_url()))
   
    def get_url(self):
        return reverse(self.url_view)


class ManagersWorkboardTests(BaseWorkboardsTestCase):
    url_view = 'url_managers_workboard'

    def test_as_president_get(self):
        super().as_president_get()

    def test_as_members_get(self):
        response_client2 = self.client2.get(
            reverse(self.url_view))
        self.assertEqual(response_client2.status_code, 403)

    def test_offline_user_redirection(self):
        super().offline_user_redirection()
