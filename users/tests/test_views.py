from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.urls import reverse

from users.models import User


class BaseUserTest(TestCase):
    def setUp(self):
        group_gadz = Group.objects.create(name='gadzarts')
        group_ext = Group.objects.create(name='externals')
        group_ext.permissions.set([])

        self.user1 = User.objects.create(username='user1')
        self.user1.groups.add(group_gadz)
        self.user2 = User.objects.create(username='user2')
        self.user2.groups.add(group_ext)
        self.user3 = User.objects.create(username='user3')
        self.client1 = Client()
        self.client1.force_login(self.user1)        
        self.client2 = Client()
        self.client2.force_login(self.user2)



class UserRetrieveViewTest(BaseUserTest):
    def test_get(self):
        # Check normal access
        response_client1 = self.client1.get(reverse('url_user_retrieve', kwargs={'group_name': 'gadzarts', 'pk': '1'}))
        self.assertEqual(response_client1.status_code, 200)
        # Check restricted access
        # response_client2 = self.client2.get(reverse('url_user_retrieve', kwargs={'group_name': 'externals', 'pk': '1'}))
        # self.assertEqual(response_client2.status_code, 403)
        # Check Redirection
        response_hacker = Client().get(reverse('url_user_retrieve', kwargs={'group_name': 'gadzarts', 'pk': '1'}))
        self.assertEqual(response_hacker.status_code, 302)
        self.assertRedirects(response_hacker, '/auth/login/')
        

class UserSelfDeactivateViewTest(BaseUserTest):
    def test_get(self):
        # Check normal access
        response_client = self.client1.get(reverse('url_self_deactivate', kwargs={'group_name': 'gadzarts', 'pk': str(self.user1.pk)}))
        self.assertEqual(response_client.status_code, 200)
        # Check Redirection
        response_hacker = Client().get(reverse('url_self_deactivate', kwargs={'group_name': 'gadzarts', 'pk': str(self.user1.pk)}))
        self.assertEqual(response_hacker.status_code, 302)
        self.assertRedirects(response_hacker, '/auth/login/')