from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class ConfigurationsNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named configurations URLs should be reversible"
        expected_named_urls = [
            ('url_index_config', [], {}),
            ('url_center_config', [], {}),
            ('url_price_config', [], {}),
            ('url_lydia_config', [], {}),
            ('url_balance_config', [], {})
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail("Reversal of url named '%s' failed with NoReverseMatch" % name)
