from django.test import Client, TestCase
from django.urls import NoReverseMatch, reverse


class UsersNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named users URLs should be reversible"
        expected_named_urls = [
            ('url_user_list', [], {}),
            ('url_user_create', [], {}),
            ('url_user_retrieve', [], {'user_pk': 53}),
            ('url_user_update', [], {'user_pk': 53}),
            ('url_user_deactivate', [], {'user_pk': 53}),
            ('url_group_update', [], {'group_pk': 53}),
            ('url_ajax_username_from_username_part', [], {}),
            ('url_balance_from_username', [], {}),
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail("Reversal of url named '%s' failed with NoReverseMatch" % name)
