from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class StocksNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named stocks URLs should be reversible"
        expected_named_urls = [
            ('url_stockentry_list', [], {'shop_pk': 53}),
            ('url_stockentry_create', [], {'shop_pk': 53}),
            ('url_stockentry_retrieve', [], {'shop_pk': 53, 'stockentry_pk': 53}),
            ('url_inventory_list', [], {'shop_pk': 53}),
            ('url_inventory_create', [], {'shop_pk': 53}),
            ('url_inventory_retrieve', [], {'shop_pk': 53, 'inventory_pk': 53})
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail("Reversal of url named '%s' failed with NoReverseMatch" % name)
