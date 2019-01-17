from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class EventsNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named events URLs should be reversible"
        expected_named_urls = [
            ('url_event_list', [], {}),
            ('url_event_create', [], {}),
            ('url_event_update', [], {'pk': 53}),
            ('url_event_finish', [], {'pk': 53}),
            ('url_event_delete', [], {'pk': 53}),
            ('url_event_self_registration', [], {'pk': 53}),
            ('url_event_manage_users', [], {'pk': 53}),
            ('url_event_remove_user', [], {'pk': 53, 'user_pk': 53}),
            ('url_event_change_weight', [], {'pk': 53, 'user_pk': 53}),
            ('url_event_download_xlsx', [], {'pk': 53}),
            ('url_event_upload_xlsx', [], {'pk': 53})
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail("Reversal of url named '%s' failed with NoReverseMatch" % name)
