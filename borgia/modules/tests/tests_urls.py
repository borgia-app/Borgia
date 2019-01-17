from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class ModulesNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named modules URLs should be reversible"
        expected_named_urls = [
            ('url_shop_module_sale', [], {'shop_pk': 53, 'module_class': 'self_sales'}),
            ('url_shop_module_config', [], {'shop_pk': 53, 'module_class': 'self_sales'}),
            ('url_shop_module_config_update', [], {'shop_pk': 53, 'module_class': 'self_sales'}),
            ('url_shop_module_category_create', [], {'shop_pk': 53, 'module_class': 'self_sales'}),
            ('url_shop_module_category_update', [], {'shop_pk': 53, 'module_class': 'self_sales', 'category_pk': 53}),
            ('url_shop_module_category_delete', [], {'shop_pk': 53, 'module_class': 'self_sales', 'category_pk': 53})
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail("Reversal of url named '%s' failed with NoReverseMatch" % name)
