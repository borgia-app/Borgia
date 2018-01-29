import unittest
from django.test import TestCase

from django.core.exceptions import ObjectDoesNotExist

from users.models import User, list_year, user_from_token_tap
from users.models import token_tap_to_token_id
from finances.models import BankAccount, Sale, SharedEvent
from django.contrib.contenttypes.models import ContentType


# class MiscellaneousUtilsUserTokenTestCase(TestCase):
#     def test_token_tap_to_token_id_valid_example(self):
#         self.assertEqual(token_tap_to_token_id('25166484851706966556857503'),
#                          '3FEB7D')
#         self.assertEqual(token_tap_to_token_id('25166484852565553687068573'),
#                          '4875DF')
#         self.assertRegexpMatches(
#             token_tap_to_token_id('25166484852565553687068573'),
#             '^[0-9A-Z]{6}$')
#
#     def test_token_tap_to_token_id_unvalid_inputs(self):
#         self.assertRaises(ValueError, token_tap_to_token_id, '12345')
#         self.assertRaises(ValueError, token_tap_to_token_id, 'ABCDE')
#         self.assertRaises(ValueError, token_tap_to_token_id,
#                           '1234567890123456789012345X')
#
#     def test_user_from_token_tap(self):
#         user1 = User.objects.create(username='user1', token_id='3FEB7D')
#         self.assertEqual(user_from_token_tap('25166484851706966556857503'),
#                          user1)
#         self.assertRaises(ObjectDoesNotExist, user_from_token_tap,
#                           '25166484852565553687068573')
#
#
# class MiscellaneousUtilsListYearTestCase(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create(username='user1', year=2010)
#         self.user2 = User.objects.create(username='user2', year=2011)
#         self.user3 = User.objects.create(username='user3', year=2016)
#         self.user4 = User.objects.create(username='user4', year=1901)
#
#     def test_list_year(self):
#         self.assertListEqual(list_year(), [2016, 2011, 2010, 1901])
#

class UserTestCase(TestCase):
    def setUp(self):
        self.userOnlyMandatory = User.objects.create(
            username='userOnlyMandatory')
        self.userAllUsedFields = User.objects.create(
            username='userAllUsedFields',
            password='hashhashhashhash',
            first_name='Alexandre',
            last_name='Palo',
            email='alexandre.palo@gadz.org',
            surname='Pastys',
            family='101-99',
            year=2014,
            campus='ME',
            phone='0612345678',
            token_id='4875DF',
            balance=100
            )

    def test_str(self):
        self.assertEqual(self.userOnlyMandatory.__str__(), 'undefined')
        self.assertEqual(self.userAllUsedFields.__str__(), 'Alexandre Palo')

    def test_year_pg(self):
        self.assertRaises(AttributeError, self.userOnlyMandatory.year_pg)
        self.assertEqual(self.userAllUsedFields.year_pg(), 214)

    def test_credit(self):
        initial_balance = self.userAllUsedFields.balance

        # Test errors without side effect
        self.assertRaises(ValueError, self.userAllUsedFields.credit, -1000)
        self.assertEqual(self.userAllUsedFields.balance, initial_balance)
        self.assertRaises(ValueError, self.userAllUsedFields.credit, 0)
        self.assertEqual(self.userAllUsedFields.balance, initial_balance)

        # Test balance effects
        self.userAllUsedFields.credit(1000)
        self.assertEqual(self.userAllUsedFields.balance, initial_balance+1000)

    def test_debit(self):
        initial_balance = self.userAllUsedFields.balance

        # Test errors without side effect
        self.assertRaises(ValueError, self.userAllUsedFields.debit, -1000)
        self.assertEqual(self.userAllUsedFields.balance, initial_balance)
        self.assertRaises(ValueError, self.userAllUsedFields.credit, 0)
        self.assertEqual(self.userAllUsedFields.balance, initial_balance)

        # Test balance effects
        self.userAllUsedFields.debit(1000)
        self.assertEqual(self.userAllUsedFields.balance, initial_balance-1000)

    # def test_list_transaction(self):
    #     user1 = User.objects.create(username='other1')
    #     user2 = User.objects.create(username='other2')
    #     s1 = Sale.objects.create(
    #         sender=self.userAllUsedFields,
    #         recipient=user1, operator=user2,
    #         content_type = ContentType.objects.get(app_label='users', model='user'),
    #         module_id = 1,
    #         ...
    #         )
    #     s2 = Sale.objects.create(
    #         sender=user1, recipient=self.userAllUsedFields, operator=user2)
    #     s3 = Sale.objects.create(
    #         sender=user1, recipient=user2, operator=self.userAllUsedFields)
    #     s4 = Sale.objects.create(
    #         sender=user1, recipient=user2, operator=self.userOnlyMandatory)
    #     s5 = Sale.objects.create(
    #         sender=self.userAllUsedFields, recipient=user1, operator=user2)
    #     s6 = Sale.objects.create(
    #         sender=self.userAllUsedFields, recipient=user1, operator=user2)
    #     se1 = SharedEvent.objects.create(
    #         description='only participant',
    #         manager=user1,
    #         sale=s4)
    #     se1.participants.add(self.userAllUsedFields)
    #     se2 = SharedEvent.objects.create(
    #         description='only manager',
    #         manager=self.userAllUsedFields,
    #         sale=s5)
    #     se3 = SharedEvent.objects.create(
    #         description='manager & participant',
    #         manager=self.userAllUsedFields,
    #         sale=s6)
    #     se3.participants.add(self.userAllUsedFields)
    #
    #     self.assertCountEqual(self.userAllUsedFields.list_sale(),
    #                           [s1, s2, s4, s6])

    # def test_list_bank_account(self):
    #     b1 = BankAccount.objects.create(
    #         bank='bank1',
    #         account='1234567891',
    #         owner=self.userAllUsedFields)
    #     b2 = BankAccount.objects.create(
    #         bank='bank2',
    #         account='1234567892',
    #         owner=self.userAllUsedFields)
    #
    #     self.assertCountEqual(self.userAllUsedFields.list_bank_account(),
    #                           [b1, b2])
    #     self.assertCountEqual(self.userOnlyMandatory.list_bank_account(), [])
