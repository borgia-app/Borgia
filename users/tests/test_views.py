from django.test import Client, TestCase
from django.urls import reverse


class BaseUserTest(TestCase):
    def setUp(self):
        self.client = Client()


class UserRetrieveViewTest(BaseUserTest):

    def test_get(self):
        response = self.client.get(reverse('url_user_retrieve', kwargs={'group_name': 'gadzarts', 'pk': '3'}))
        # self.assertEqual(response.status_code, 200)
