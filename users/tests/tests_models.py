from django.test import TestCase

from users.models import User, get_list_year


class UserTest(TestCase):
    def setUp(self):
        self.user_only_username = User.objects.create(
            username='userOnlyUsername')
        self.user_all_fields = User.objects.create(
            username='userAllFields',
            password='password',
            first_name='firstName',
            last_name='lastName',
            email='email.email@gadz.org',
            surname='surname',
            family='53',
            year=2015,
            campus='ME',
            phone='0600000000',
            balance=100
        )
        self.user_with_first_name = User.objects.create(
            username='userWithFirstName',
            first_name='AReallyCoolFirstName')
        self.user_with_last_name = User.objects.create(
            username='userWithLastName',
            last_name='AnAmazingLastName')

    def test_str(self):
        self.assertEqual(self.user_only_username.__str__(), 'userOnlyUsername')
        self.assertEqual(self.user_all_fields.__str__(), 'firstName lastName')
        self.assertEqual(self.user_with_first_name.__str__(),
                         'userWithFirstName')
        self.assertEqual(self.user_with_last_name.__str__(),
                         'userWithLastName')

    def test_get_full_name(self):
        self.assertEqual(self.user_only_username.get_full_name(), 'userOnlyUsername')
        self.assertEqual(self.user_all_fields.get_full_name(), 'surname 53ME215')
        self.assertEqual(self.user_with_first_name.get_full_name(),
                         'userWithFirstName')
        self.assertEqual(self.user_with_last_name.get_full_name(),
                         'userWithLastName')

    def test_year_pg(self):
        self.assertEqual(self.user_all_fields.year_pg(), "215")
        self.assertEqual(self.user_only_username.year_pg(), "")

    def test_credit(self):
        initial_balance = self.user_all_fields.balance

        # Test errors without side effect
        self.assertRaises(ValueError, self.user_all_fields.credit, -1000)
        self.assertEqual(self.user_all_fields.balance, initial_balance)
        self.assertRaises(ValueError, self.user_all_fields.credit, 0)
        self.assertEqual(self.user_all_fields.balance, initial_balance)

        # Test balance effects
        self.user_all_fields.credit(1000)
        self.assertEqual(self.user_all_fields.balance, initial_balance + 1000)

    def test_debit(self):
        initial_balance = self.user_all_fields.balance

        # Test errors without side effect
        self.assertRaises(ValueError, self.user_all_fields.debit, -1000)
        self.assertEqual(self.user_all_fields.balance, initial_balance)
        self.assertRaises(ValueError, self.user_all_fields.credit, 0)
        self.assertEqual(self.user_all_fields.balance, initial_balance)

        # Test balance effects
        self.user_all_fields.debit(20)
        self.assertEqual(self.user_all_fields.balance, initial_balance - 20)

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
    #         sender=user1, recipient=user2, operator=self.userOnlyUsername)
    #     s5 = Sale.objects.create(
    #         sender=self.userAllUsedFields, recipient=user1, operator=user2)
    #     s6 = Sale.objects.create(
    #         sender=self.userAllUsedFields, recipient=user1, operator=user2)
    #     se1 = Event.objects.create(
    #         description='only participant',
    #         manager=user1,
    #         sale=s4)
    #     se1.participants.add(self.userAllUsedFields)
    #     se2 = Event.objects.create(
    #         description='only manager',
    #         manager=self.userAllUsedFields,
    #         sale=s5)
    #     se3 = Event.objects.create(
    #         description='manager & participant',
    #         manager=self.userAllUsedFields,
    #         sale=s6)
    #     se3.participants.add(self.userAllUsedFields)
    #
    #     self.assertCountEqual(self.userAllUsedFields.list_sale(),
    #                           [s1, s2, s4, s6])


class ListYearTest(TestCase):
    """
    Be careful : user1 is ignored (in the current BDD, user1 is the admin)
    """
    def setUp(self):
        self.user1 = User.objects.create(username='user1', year=2010)
        self.user2 = User.objects.create(username='user2', year=2011)
        self.user3 = User.objects.create(username='user3', year=2016)
        self.user4 = User.objects.create(username='user4', year=1901)

    def test_list_year(self):
        self.assertListEqual(get_list_year(), [2016, 2011, 1901])
