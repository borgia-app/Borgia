from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class FinancesNamedURLTests(TestCase):

    def test_named_urls(self):
        "Named finances URLs should be reversible"
        expected_named_urls = [
            ('url_self_transaction_list', [], {}),
            ('url_user_exceptionnalmovement_create', [], {'user_pk': 53}),
            ('url_recharging_create', [], {'user_pk': 53}),
            ('url_recharging_list', [], {}),
            ('url_recharging_retrieve', [], {'recharging_pk': 53}),
            ('url_transfert_list', [], {}),
            ('url_transfert_create', [], {}),
            ('url_transfert_retrieve', [], {'transfert_pk': 53}),
            ('url_exceptionnalmovement_list', [], {}),
            ('url_exceptionnalmovement_retrieve',
             [], {'exceptionnalmovement_pk': 53}),
            ('url_self_lydia_create', [], {}),
            ('url_self_lydia_confirm', [], {}),
            ('url_self_lydia_callback', [], {})
        ]
        for name, args, kwargs in expected_named_urls:
            with self.subTest(name=name):
                try:
                    reverse(name, args=args, kwargs=kwargs)
                except NoReverseMatch:
                    self.fail(
                        "Reversal of url named '%s' failed with NoReverseMatch" % name)
