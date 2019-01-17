import datetime
import decimal

from django.test import TestCase

from events.models import Event
from users.models import User


class EventModelTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create(
            username='username_manager',
            last_name='Last name manager',
            first_name='First name manager'
        )

        self.event1 = Event.objects.create(
            description='Test53',
            date=datetime.date(2053, 1, 1),
            manager=self.manager,
            price=decimal.Decimal(1000.00)
        )
        self.user1 = User.objects.create(
            username='user1',
            last_name='Last name 1',
            first_name='First name 1',
            balance=1000
        )
        self.user2 = User.objects.create(
            username='user2',
            last_name='Last name 2',
            first_name='First name 2',
            balance=2000
        )
        self.user3 = User.objects.create(
            username='user3',
            last_name='Last name 3',
            first_name='First name 3',
            balance=3000
        )
        self.user4 = User.objects.create(
            username='user4',
            last_name='Last name 4',
            first_name='First name 4',
            balance=4000
        )
        self.banker = User.objects.create(
            username='Banker',
            last_name='Ker',
            first_name='Ban',
            balance=0
        )

    def test_add_and_remove_user(self):
        # INIT
        self.event1.change_weight(self.user1, 100, is_participant=True)
        self.event1.change_weight(self.user1, 30, is_participant=True)
        self.event1.add_weight(self.user1, 23, is_participant=True)
        self.event1.change_weight(self.user1, 10, is_participant=False)
        self.event1.change_weight(self.user1, 1, is_participant=False)
        self.event1.add_weight(self.user1, 2, is_participant=False)
        # User 1 now should have 3 in registration, and 53 in participation
        self.event1.add_weight(self.user2, 200, is_participant=False)
        self.event1.add_weight(self.user2, 2, is_participant=False)
        # User 2 now should have 202 in registration
        self.event1.add_weight(self.user3, 400, is_participant=True)
        self.event1.change_weight(self.user3, 47, is_participant=True)
        # User 3 now should have 303 in participation
        registration_u1 = self.event1.get_weight_of_user(
            self.user1, is_participant=False)
        participation_u1 = self.event1.get_weight_of_user(
            self.user1, is_participant=True)
        registration_u2 = self.event1.get_weight_of_user(
            self.user2, is_participant=False)
        participation_u2 = self.event1.get_weight_of_user(
            self.user2, is_participant=True)
        registration_u3 = self.event1.get_weight_of_user(
            self.user3, is_participant=False)
        participation_u3 = self.event1.get_weight_of_user(
            self.user3, is_participant=True)
        registration_u4 = self.event1.get_weight_of_user(
            self.user4, is_participant=False)
        participation_u4 = self.event1.get_weight_of_user(
            self.user4, is_participant=True)

        # TESTS
        self.assertEqual(registration_u1, 3)
        self.assertEqual(participation_u1, 53)

        self.assertEqual(registration_u2, 202)
        self.assertEqual(participation_u2, 0)

        self.assertEqual(registration_u3, 0)
        self.assertEqual(participation_u3, 47)

        self.assertEqual(registration_u4, 0)
        self.assertEqual(participation_u4, 0)

        # END
        self.event1.remove_user(self.user1)
        self.event1.remove_user(self.user2)
        self.event1.remove_user(self.user3)
        self.event1.remove_user(self.user4)

        self.assertEqual(self.event1.get_weight_of_user(
            self.user1, is_participant=False), 0)
        self.assertEqual(self.event1.get_weight_of_user(
            self.user1, is_participant=True), 0)
        self.assertEqual(self.event1.get_weight_of_user(
            self.user2, is_participant=False), 0)
        self.assertEqual(self.event1.get_weight_of_user(
            self.user2, is_participant=True), 0)
        self.assertEqual(self.event1.get_weight_of_user(
            self.user3, is_participant=False), 0)
        self.assertEqual(self.event1.get_weight_of_user(
            self.user3, is_participant=True), 0)
        self.assertEqual(self.event1.get_weight_of_user(
            self.user4, is_participant=False), 0)
        self.assertEqual(self.event1.get_weight_of_user(
            self.user4, is_participant=True), 0)

    def test_get_price_of_user(self):
        # INIT
        self.event1.change_weight(self.user1, 9, True)
        self.event1.change_weight(self.user2, 1, True)
        # TESTS
        # Reminder: price = 1000
        self.assertEqual(self.event1.get_price_of_user(self.user1), 900)
        self.assertEqual(self.event1.get_price_of_user(self.user2), 100)
        # END
        self.event1.remove_user(self.user1)
        self.event1.remove_user(self.user2)

    def test_get_total_weights(self):
        # INIT
        self.event1.change_weight(self.user1, 10, is_participant=True)
        self.event1.change_weight(self.user1, 5, is_participant=False)
        self.event1.change_weight(self.user2, 40, is_participant=True)
        self.event1.change_weight(self.user2, 25, is_participant=False)
        # TESTS
        self.assertEqual(self.event1.get_total_weights_registrants(), 30)
        self.assertEqual(self.event1.get_total_weights_participants(), 50)
        # END
        self.event1.remove_user(self.user1)
        self.event1.remove_user(self.user2)

    def test_get_total_users(self):
        # INIT
        self.event1.change_weight(self.user1, 10, is_participant=True)
        self.event1.change_weight(self.user1, 5, is_participant=False)
        self.event1.change_weight(self.user2, 40, is_participant=True)
        # TESTS
        self.assertEqual(self.event1.get_number_registrants(), 1)
        self.assertEqual(self.event1.get_number_participants(), 2)
        # END
        self.event1.remove_user(self.user1)
        self.event1.remove_user(self.user2)

    def test_pay_by_total(self):
        # INIT
        event_total_price = Event.objects.create(
            description='Test_payment',
            date=datetime.date(2053, 1, 1),
            manager=self.manager,
            price=decimal.Decimal(1000.00)
        )
        user1_initial_balance = self.user1.balance
        user2_initial_balance = self.user2.balance
        banker_initial_balance = self.banker.balance

        event_total_price.change_weight(self.user1, 10, is_participant=True)
        event_total_price.change_weight(self.user2, 5, is_participant=False)
        event_total_price.change_weight(self.user2, 40, is_participant=True)
        event_total_price.pay_by_total(self.manager, self.banker, decimal.Decimal(100.00))

        # Get users with updated balance
        self.user1 = User.objects.get(pk=self.user1.pk)
        self.user2 = User.objects.get(pk=self.user2.pk)

        # TESTS
        self.assertEqual(event_total_price.done, True)
        self.assertEqual(event_total_price.payment_by_ponderation, False)
        self.assertEqual(self.banker.balance, banker_initial_balance + 100)
        self.assertEqual(event_total_price.price, 100)
        self.assertEqual(
            event_total_price.remark, 'Paiement par Borgia (Prix total : 100)')
        self.assertEqual(self.user1.balance, user1_initial_balance - 20)
        self.assertEqual(self.user2.balance, user2_initial_balance - 80)

    def test_pay_by_ponderation(self):
        # INIT
        event_pond_price = Event.objects.create(
            description='Test_payment',
            date=datetime.date(2053, 1, 1),
            manager=self.manager,
            price=decimal.Decimal(150.0)
        )
        user1_initial_balance = self.user1.balance
        user2_initial_balance = self.user2.balance
        banker_initial_balance = self.banker.balance

        event_pond_price.change_weight(self.user1, 10, is_participant=True)
        event_pond_price.change_weight(self.user2, 5, is_participant=False)
        event_pond_price.change_weight(self.user2, 40, is_participant=True)
        event_pond_price.pay_by_ponderation(self.manager, self.banker, 3)

        # Get users with updated balance
        self.user1 = User.objects.get(pk=self.user1.pk)
        self.user2 = User.objects.get(pk=self.user2.pk)

        # TESTS
        self.assertEqual(event_pond_price.done, True)
        self.assertEqual(event_pond_price.payment_by_ponderation, True)
        self.assertEqual(event_pond_price.price, decimal.Decimal(3.00))
        self.assertEqual(self.banker.balance, banker_initial_balance + 150)
        self.assertEqual(
            event_pond_price.remark, 'Paiement par Borgia (Prix par pondération: 3)')
        self.assertEqual(self.user1.balance, user1_initial_balance - 30)
        self.assertEqual(self.user2.balance, user2_initial_balance - 120)
