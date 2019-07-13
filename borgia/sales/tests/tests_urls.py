from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class SalesNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named sales URLs should be reversible"
        expected_named_urls = [
            ('url_sale_list', [], {'shop_pk': 53}),
            ('url_sale_retrieve', [], {'shop_pk': 53, 'sale_pk': 53})
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail(
                        "Reversal of url named '%s' failed with NoReverseMatch" % name)
