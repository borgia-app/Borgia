import random
from django.test import TestCase

from users.models import User, get_list_year
from borgia.tests.utils import fake_User


class UserTest(TestCase):
    def setUp(self):
        self.user_only_username = fake_User(['username'])
        self.user_all_fields = fake_User()
        self.user_with_first_name = fake_User(['username', 'first_name'])
        self.user_with_last_name = fake_User(['username', 'last_name'])
        self.user_with_forced_year = fake_User(
            ['username', 'campus'], {'year': '2014'})

    def test_str(self):
        self.assertEqual(self.user_only_username.__str__(),
                         self.user_only_username.username)
        self.assertEqual(self.user_all_fields.__str__(
        ), f'{self.user_all_fields.first_name} {self.user_all_fields.last_name}')
        self.assertEqual(self.user_with_first_name.__str__(),
                         self.user_with_first_name.username)
        self.assertEqual(self.user_with_last_name.__str__(),
                         self.user_with_last_name.username)

    def test_get_full_name(self):
        self.assertEqual(
            self.user_only_username.get_full_name(), self.user_only_username.username)
        self.assertEqual(self.user_all_fields.get_full_name(),
                         f'{self.user_all_fields.surname} {self.user_all_fields.family}{self.user_all_fields.campus}{self.user_all_fields.year_pg()}')
        self.assertEqual(self.user_with_first_name.get_full_name(),
                         self.user_with_first_name.username)
        self.assertEqual(self.user_with_last_name.get_full_name(),
                         self.user_with_last_name.username)

    def test_year_pg(self):
        self.assertEqual(self.user_with_forced_year.year_pg(), "214")
        self.assertEqual(self.user_only_username.year_pg(), "")

    def test_credit(self):
        initial_balance = self.user_all_fields.balance

        # Test errors without side effect
        self.assertRaises(
            ValueError, self.user_all_fields.credit, random.uniform(-1000, 0))
        self.assertEqual(self.user_all_fields.balance, initial_balance)
        self.assertRaises(ValueError, self.user_all_fields.credit, 0)
        self.assertEqual(self.user_all_fields.balance, initial_balance)

        # Test balance effects
        valid_credit = random.uniform(0, 1000)
        self.user_all_fields.credit(valid_credit)
        self.assertEqual(self.user_all_fields.balance,
                         initial_balance + valid_credit)

    def test_debit(self):
        initial_balance = self.user_all_fields.balance

        # Test errors without side effect
        self.assertRaises(ValueError, self.user_all_fields.debit,
                          random.uniform(-1000, 0))
        self.assertEqual(self.user_all_fields.balance, initial_balance)
        self.assertRaises(ValueError, self.user_all_fields.credit, 0)
        self.assertEqual(self.user_all_fields.balance, initial_balance)

        # Test balance effects

        valid_debit = random.uniform(0, 1000)
        self.user_all_fields.debit(valid_debit)
        self.assertEqual(self.user_all_fields.balance,
                         initial_balance - valid_debit)


class ListYearTest(TestCase):
    """
    Be careful : the first user is ignored, considered as the admin.
    """

    def setUp(self):
        self.years = [random.randrange(2000, 2999)
                      for _ in range(0, random.randrange(5, 20))]

        for y in self.years:
            fake_User(['username'], {'year': y})

    def test_list_year(self):

        # compare to the list of unique values
        unique_years = sorted(list(dict.fromkeys(self.years)), reverse=True)
        # remove pk=1 user's year if he's the only one to have this year
        if self.years.count(self.years[0]) == 1:
            unique_years.remove(self.years[0])

        self.assertListEqual(get_list_year(), unique_years)
