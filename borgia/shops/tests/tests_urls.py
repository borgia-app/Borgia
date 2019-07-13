"""
Test for shops named urls
"""
from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class ShopsNamedURLTests(TestCase):
    """
    Test for shops named urls
    """

    def test_named_urls(self):
        "Named shops URLs should be reversible"
        expected_named_urls = [
            ('url_shop_list', [], {}),
            ('url_shop_create', [], {}),
            ('url_shop_update', [], {'shop_pk': 53}),
            ('url_shop_checkup', [], {'shop_pk': 53}),
            ('url_shop_workboard', [], {'shop_pk': 53})
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail(
                        "Reversal of url named '%s' failed with NoReverseMatch" % name)


class ShopProductsNamedURLTests(TestCase):
    """
    Test for shop products named urls
    """

    def test_named_urls(self):
        "Named products URLs should be reversible"
        expected_named_urls = [
            ('url_product_list', [], {'shop_pk': 53}),
            ('url_product_create', [], {'shop_pk': 53}),
            ('url_product_retrieve', [], {'shop_pk': 53, 'product_pk': 53}),
            ('url_product_update', [], {'shop_pk': 53, 'product_pk': 53}),
            ('url_product_update_price', [], {
             'shop_pk': 53, 'product_pk': 53}),
            ('url_product_deactivate', [], {'shop_pk': 53, 'product_pk': 53}),
            ('url_product_remove', [], {'shop_pk': 53, 'product_pk': 53})
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail(
                        "Reversal of url named '%s' failed with NoReverseMatch" % name)
