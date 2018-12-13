from django.urls import reverse
from django.test import TestCase


class UserUrlsTest(TestCase):
    """Test URL patterns for users app."""

    def test_url_user_list(self):
        self.assertEqual(reverse('url_user_list',
                                 kwargs={'group_name': 'group_name'}),
                         '/group_name/users/')

    def test_url_user_create(self):
        self.assertEqual(reverse('url_user_create',
                                 kwargs={'group_name': 'group_name'}),
                         '/group_name/users/create/')

    def test_url_user_retrieve(self):
        self.assertEqual(reverse('url_user_retrieve',
                                 kwargs={'group_name': 'group_name', 'pk': '53'}),
                         '/group_name/users/53/')

    def test_url_user_update(self):
        self.assertEqual(reverse('url_user_update',
                                 kwargs={'group_name': 'group_name', 'pk': '53'}),
                         '/group_name/users/53/update/')

    def test_url_user_deactivate(self):
        self.assertEqual(reverse('url_user_deactivate',
                                 kwargs={'group_name': 'group_name', 'pk': '53'}),
                         '/group_name/users/53/deactivate/')

    def test_url_self_deactivate(self):
        self.assertEqual(reverse('url_self_deactivate',
                                 kwargs={'group_name': 'group_name', 'pk': '53'}),
                         '/group_name/users/53/self_deactivate/')

    def test_url_self_user_update(self):
        self.assertEqual(reverse('url_user_self_update',
                                 kwargs={'group_name': 'group_name'}),
                         '/group_name/users/self/')

    def test_url_group_update(self):
        self.assertEqual(reverse('url_group_update',
                                 kwargs={'group_name': 'group_name', 'pk': '53'}),
                         '/group_name/groups/53/update/')

    def test_url_ajax_username_from_username_part(self):
        self.assertEqual(reverse('url_ajax_username_from_username_part'),
                         '/ajax/username_from_username_part/')

    def test_url_balance_from_username(self):
        self.assertEqual(reverse('url_balance_from_username'),
                         '/ajax/balance_from_username/')
