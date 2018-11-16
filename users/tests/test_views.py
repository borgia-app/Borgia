from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import reverse

from users.models import User


class BaseUsersViewsTest(TestCase):
    def setUp(self):
        members_group = Group.objects.create(name='gadzarts')
        presidents_group = Group.objects.create(name='presidents')
        presidents_group.permissions.set(Permission.objects.all())
        # Group specials NEED to be created (else raises errors) :
        specials_group = Group.objects.create(name='specials')
        specials_group.permissions.set([])

        self.user1 = User.objects.create(username='user1', balance=53)
        self.user1.groups.add(members_group)
        self.user1.groups.add(presidents_group)
        self.user2 = User.objects.create(username='user2', balance=144)
        self.user2.groups.add(specials_group)
        self.user3 = User.objects.create(username='user3')
        self.client1 = Client()
        self.client1.force_login(self.user1)
        self.client2 = Client()
        self.client2.force_login(self.user2)
        self.client3 = Client()
        self.client3.force_login(self.user3)


class UserListViewTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_list', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserCreateViewTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_create', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_create', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserRetrieveViewTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_retrieve', kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_retrieve', kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserUpdateViewTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_update', kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_update', kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserDeactivateViewTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_deactivate', kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_deactivate', kwargs={'group_name': 'presidents', 'pk': '2'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserSelfDeactivateViewTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client = self.client1.get(reverse('url_self_deactivate', kwargs={'group_name': 'gadzarts', 'pk': str(self.user1.pk)}))
        self.assertEqual(response_client.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_self_deactivate', kwargs={'group_name': 'gadzarts', 'pk': str(self.user1.pk)}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class UserSelfUpdateViewTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_user_self_update', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_user_self_update', kwargs={'group_name': 'presidents'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')


class ManageGroupViewTest(BaseUsersViewsTest):
    def test_get_allowed_user(self):
        response_client1 = self.client1.get(reverse('url_group_update', kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)

    def test_offline_user_redirection(self):
        response_offline_user = Client().get(reverse('url_group_update', kwargs={'group_name': 'presidents', 'pk': '1'}))
        self.assertEqual(response_offline_user.status_code, 302)
        self.assertRedirects(response_offline_user, '/auth/login/')
