import unittest
from datetime import date
from decimal import Decimal
from django.test import TestCase

from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from shops.models import *
from finances.models import *


class LydiaTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            last_name='Last name 1',
            first_name='First name 1'
        )
        self.user2 = User.objects.create(
            username='user2'
        )
        self.lydia = Lydia.objects.create(
            amount=10,
            id_from_lydia='abcdefg',
            sender=self.user1,
            recipient=self.user2
        )
        self.payment = Payment.objects.create()
        self.payment.lydias.add(self.lydia)
        self.payment.maj_amount()
        self.sale = Sale.objects.create(
            wording='',
            sender=self.user1,
            recipient=self.user2,
            operator=self.user1,
            payment=self.payment
        )
        self.sale.maj_amount()

    def test_str(self):
        self.assertEqual(
            self.lydia.__str__(),
            'Last name 1 First name 1 10€')

    def test_list_transaction(self):
        self.assertCountEqual(
            self.lydia.list_transaction(),
            [self.sale]
        )


class CashTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            last_name='Last name 1',
            first_name='First name 1'
        )
        self.user2 = User.objects.create(
            username='user2'
        )
        self.cash = Cash.objects.create(
            amount=10,
            sender=self.user1,
            recipient=self.user2
        )
        self.payment = Payment.objects.create()
        self.payment.cashs.add(self.cash)
        self.payment.maj_amount()
        self.sale = Sale.objects.create(
            wording='',
            sender=self.user1,
            recipient=self.user2,
            operator=self.user1,
            payment=self.payment
        )
        self.sale.maj_amount()

    def test_str(self):
        self.assertEqual(
            self.cash.__str__(),
            'Last name 1 First name 1 10€')

    def test_list_sale(self):
        self.assertCountEqual(
            self.cash.list_sale(),
            [self.sale]
        )

    def test_list_payment(self):
        self.assertCountEqual(
            self.cash.list_payment(),
            [self.payment]
        )


class ChequeTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            last_name='Last name 1',
            first_name='First name 1'
        )
        self.user2 = User.objects.create(
            username='user2'
        )
        self.bank_account = BankAccount.objects.create(
            bank='bank',
            account='account',
            owner=self.user1
        )
        self.cheque = Cheque.objects.create(
            amount=10,
            cheque_number='1234567',
            sender=self.user1,
            recipient=self.user2,
            bank_account=self.bank_account
        )
        self.payment = Payment.objects.create()
        self.payment.cheques.add(self.cheque)
        self.payment.maj_amount()
        self.sale = Sale.objects.create(
            wording='',
            sender=self.user1,
            recipient=self.user2,
            operator=self.user1,
            payment=self.payment
        )
        self.sale.maj_amount()

    def test_str(self):
        self.assertEqual(
            self.cheque.__str__(),
            'Last name 1 First name 1 10€ n°1234567')

    def test_list_sale(self):
        self.assertCountEqual(
            self.cheque.list_sale(),
            [self.sale]
        )

    def test_list_payments(self):
        self.assertCountEqual(
            self.cheque.list_payments(),
            [self.payment]
        )


class DebitBalanceTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            last_name='Last name 1',
            first_name='First name 1'
        )
        self.user2 = User.objects.create(
            username='user2'
        )
        self.debit_balance = DebitBalance.objects.create(
            amount=10,
            date=date.today(),
            sender=self.user1,
            recipient=self.user2
        )

    def test_str(self):
        self.assertEqual(
            self.debit_balance.__str__(),
            '10€ ' + str(date.today()))

    def test_set_movement(self):
        self.user1.balance = 100
        self.user1.save()
        self.debit_balance.set_movement()
        self.assertAlmostEqual(
            self.user1.balance,
            Decimal(90)
        )
        self.assertAlmostEqual(
            self.user2.balance,
            Decimal(0)
        )


class BankAccountTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            last_name='Last name 1',
            first_name='First name 1'
        )
        self.user2 = User.objects.create(
            username='user2'
        )
        self.bank_account = BankAccount.objects.create(
            bank='bank',
            account='account',
            owner=self.user1
        )

    def test_str(self):
        self.assertEqual(
            self.bank_account.__str__(),
            'bank account'
        )


class PaymentTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            last_name='Last name 1',
            first_name='First name 1'
        )
        self.user2 = User.objects.create(
            username='user2'
        )
        self.bank_account = BankAccount.objects.create(
            bank='bank',
            account='account',
            owner=self.user1
        )
        self.cheque = Cheque.objects.create(
            amount=10,
            cheque_number='1234567',
            sender=self.user1,
            recipient=self.user2,
            bank_account=self.bank_account
        )
        self.debit_balance = DebitBalance.objects.create(
            amount=10,
            date=date.today(),
            sender=self.user1,
            recipient=self.user2
        )
        self.cash = Cash.objects.create(
            amount=10,
            sender=self.user1,
            recipient=self.user2
        )
        self.lydia = Lydia.objects.create(
            amount=10,
            id_from_lydia='abcdefg',
            sender=self.user1,
            recipient=self.user2
        )
        self.payment = Payment.objects.create()
        self.payment.cheques.add(self.cheque)
        self.payment.debit_balance.add(self.debit_balance)
        self.payment.cashs.add(self.cash)
        self.payment.lydias.add(self.lydia)

    def test_str(self):
        self.assertEqual(
            self.payment.__str__(),
            'payement n°' + str(self.payment.pk)
        )

    def test_list_cheque(self):
        self.assertCountEqual(
            self.payment.list_cheque()[0],
            [self.cheque]
        )
        self.assertAlmostEqual(
            self.payment.list_cheque()[1],
            Decimal(10)
        )

    def test_list_lydia(self):
        self.assertCountEqual(
            self.payment.list_lydia()[0],
            [self.lydia]
        )
        self.assertAlmostEqual(
            self.payment.list_lydia()[1],
            Decimal(10)
        )

    def test_list_cash(self):
        self.assertCountEqual(
            self.payment.list_cash()[0],
            [self.cash]
        )
        self.assertAlmostEqual(
            self.payment.list_cash()[1],
            Decimal(10)
        )

    def test_list_debit_balance(self):
        self.assertCountEqual(
            self.payment.list_debit_balance()[0],
            [self.debit_balance]
        )
        self.assertAlmostEqual(
            self.payment.list_debit_balance()[1],
            Decimal(10)
        )

    def test_maj_amount(self):
        self.assertAlmostEqual(
            self.payment.amount,
            Decimal(0)
        )
        self.payment.maj_amount()
        self.assertAlmostEqual(
            self.payment.amount,
            Decimal(40)
        )

    def test_payments_used(self):
        self.assertCountEqual(
            self.payment.payments_used(),
            ['Cheque', 'Espèces', 'Lydia', 'Compte foyer']
        )
        payment2 = Payment.objects.create()
        self.assertCountEqual(
            payment2.payments_used(),
            []
        )
        payment2.cashs.add(self.cash)
        self.assertCountEqual(
            payment2.payments_used(),
            ['Espèces']
        )
        payment2.cashs.remove(self.cash)
        self.assertCountEqual(
            payment2.payments_used(),
            []
        )


class SaleTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            last_name='Last name 1',
            first_name='First name 1'
            )
        self.user2 = User.objects.create(
            username='user2'
            )
        self.user3 = User.objects.create(
            username='user3'
            )
        self.shop = Shop.objects.create(
            name='Shop name',
            description='Shop description'
            )
        self.pu1 = ProductUnit.objects.create(
            name='pu1 name',
            description='pu1 description',
            unit='CL',
            type='keg'
            )
        self.pu2 = ProductUnit.objects.create(
            name='pu2 name',
            description='pu2 description',
            unit='G',
            type='meat'
            )
        self.pb1 = ProductBase.objects.create(
            name='pb1 name',
            description='pb1 description',
            manual_price=1.15,
            brand='pb1 brand',
            type='single_product',
            shop=self.shop
            )
        self.pb2 = ProductBase.objects.create(
            name='pb2 name',
            description='pb2 description',
            manual_price=150,
            brand='pb2 brand',
            type='container',
            quantity=100,
            product_unit=self.pu1,
            shop=self.shop
            )
        self.pb3 = ProductBase.objects.create(
            name='pb3 name',
            description='pb3 description',
            manual_price=150,
            brand='pb3 brand',
            type='container',
            quantity=100,
            product_unit=self.pu2,
            shop=self.shop
            )
        self.pb4 = ProductBase.objects.create(
            name='pb4 name',
            description='pb4 description shooter',
            manual_price=1.15,
            brand='pb4 brand',
            type='single_product',
            shop=self.shop
            )
        self.lydia_user1 = Lydia.objects.create(
            amount=10,
            id_from_lydia='abcdefg',
            sender=self.user1,
            recipient=self.user2
            )
        self.cash_user3 = Cash.objects.create(
            amount=6,
            sender=self.user3,
            recipient=self.user2
            )
        self.payment = Payment.objects.create()
        self.payment.lydias.add(self.lydia_user1)
        self.payment.cashs.add(self.cash_user3)
        self.payment.maj_amount()
        self.sale = Sale.objects.create(
            wording='',
            sender=self.user1,
            recipient=self.user2,
            operator=self.user1,
            payment=self.payment
            )
        self.sp_pb1 = SingleProduct.objects.create(
            price=1,
            purchase_date='2016-01-01',
            place='place sp',
            product_base=self.pb1,
            sale_price=1,
            sale=self.sale,
            is_sold=True
            )
        self.c_pb2 = Container.objects.create(
            price=100,
            purchase_date='2016-01-01',
            place='place sp',
            product_base=self.pb2
            )
        self.spfc_pb2 = SingleProductFromContainer.objects.create(
            quantity=10,
            container=self.c_pb2,
            sale_price=15,
            sale=self.sale
            )

    def test__str__(self):
        self.assertEqual(
            self.sale.__str__(),
            'Achat n°' + str(self.sale.pk)
        )

    def test_list_single_products(self):
        self.assertCountEqual(
            self.sale.list_single_products()[0],
            [self.sp_pb1]
        )
        self.assertAlmostEquals(
            self.sale.list_single_products()[1],
            Decimal(1)
        )

    def test_list_single_products_from_container(self):
        self.assertCountEqual(
            self.sale.list_single_products_from_container()[0],
            [self.spfc_pb2]
        )
        self.assertAlmostEquals(
            self.sale.list_single_products_from_container()[1],
            Decimal(15)
        )

    def test_maj_amount(self):
        self.assertAlmostEquals(
            self.sale.amount,
            Decimal(0)
        )
        self.sale.maj_amount()
        self.assertAlmostEquals(
            self.sale.amount,
            Decimal(16)
        )

    def test_price_for(self):
        self.assertAlmostEquals(
            self.sale.price_for(self.user1),
            Decimal(-10)
        )
        self.assertAlmostEquals(
            self.sale.price_for(self.user2),
            Decimal(0)
        )
        self.assertAlmostEquals(
            self.sale.price_for(self.user3),
            Decimal(-6)
        )

    def test_string_products(self):
        self.assertEqual(
            self.sale.string_products(),
            self.sp_pb1.__str__() + ', ' + self.spfc_pb2.__str__()
        )


class MiscellaneousSaleTransfertTestCase(TestCase):
    fixtures = ['shops.json', 'special_members.json']

    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            balance=100
            )
        self.user2 = User.objects.create(
            username='user2',
            balance=10
            )
        sale_transfert(
            sender=self.user1,
            recipient=self.user2,
            amount=50,
            date=date.today(),
            justification='remboursement'
        )

    def test_debit_balance(self):
        # Exceptions are directly raised if objects does not exists
        debit_balance = DebitBalance.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            debit_balance.amount,
            Decimal(50)
        )
        self.assertEquals(
            debit_balance.sender,
            self.user1
        )
        self.assertEquals(
            debit_balance.recipient,
            self.user2
        )

    def test_payment(self):
        # Exceptions are directly raised if objects does not exists
        payment = Payment.objects.all()[0]  # Theorically the only one.
        self.assertAlmostEquals(
            payment.amount,
            Decimal(50)
        )
        self.assertCountEqual(
            payment.list_cheque()[0],
            []
        )
        self.assertCountEqual(
            payment.list_lydia()[0],
            []
        )
        self.assertCountEqual(
            payment.list_cash()[0],
            []
        )
        self.assertCountEqual(
            payment.list_debit_balance()[0],
            [DebitBalance.objects.get(sender=self.user1)]
        )
        self.assertAlmostEquals(
            payment.list_cheque()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_lydia()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_cash()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_debit_balance()[1],
            Decimal(50)
        )

    def test_sale(self):
        # Exceptions are directly raised if objects does not exists
        sale = Sale.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            sale.amount,
            Decimal(50)
        )
        self.assertTrue(sale.done)
        self.assertFalse(sale.is_credit)
        self.assertEquals(
            sale.category,
            'transfert'
        )
        self.assertEquals(
            sale.wording,
            ''
        )
        self.assertEquals(
            sale.justification,
            'remboursement'
        )
        self.assertEquals(
            sale.sender,
            self.user1
        )
        self.assertEquals(
            sale.recipient,
            self.user2
        )
        self.assertEquals(
            sale.operator,
            self.user1
        )
        self.assertEquals(
            sale.payment,
            Payment.objects.all()[0]
        )

    def test_balances(self):
        self.assertAlmostEquals(
            self.user1.balance,
            Decimal(50)
        )
        self.assertAlmostEquals(
            self.user2.balance,
            Decimal(60)
        )


class MiscellaneousSaleRechargingSelfLydiaTestCase(TestCase):
    fixtures = ['shops.json', 'special_members.json']

    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            balance=100
            )
        self.lydia = Lydia.objects.create(
            date_operation=date.today(),
            amount=10,
            id_from_lydia='abcdefg',
            sender=self.user1,
            recipient=User.objects.get(username='AE_ENSAM')
            )
        sale_recharging(
            sender=self.user1,
            operator=self.user1,
            date=date.today(),
            wording='Rechargement automatique',
            payments_list=[self.lydia]
        )

    def test_payment(self):
        # Exceptions are directly raised if objects does not exists
        payment = Payment.objects.all()[0]  # Theorically the only one.
        self.assertAlmostEquals(
            payment.amount,
            Decimal(10)
        )
        self.assertCountEqual(
            payment.list_cheque()[0],
            []
        )
        self.assertCountEqual(
            payment.list_lydia()[0],
            [self.lydia]
        )
        self.assertCountEqual(
            payment.list_cash()[0],
            []
        )
        self.assertCountEqual(
            payment.list_debit_balance()[0],
            []
        )
        self.assertAlmostEquals(
            payment.list_cheque()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_lydia()[1],
            Decimal(10)
        )
        self.assertAlmostEquals(
            payment.list_cash()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_debit_balance()[1],
            Decimal(0)
        )

    def test_sale(self):
        # Exceptions are directly raised if objects does not exists
        sale = Sale.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            sale.amount,
            Decimal(10)
        )
        self.assertTrue(sale.done)
        self.assertTrue(sale.is_credit)
        self.assertEquals(
            sale.category,
            'recharging'
        )
        self.assertEquals(
            sale.wording,
            'Rechargement automatique'
        )
        self.assertIsNone(sale.justification)
        self.assertEquals(
            sale.sender,
            self.user1
        )
        self.assertEquals(
            sale.recipient,
            User.objects.get(username='AE_ENSAM')
        )
        self.assertEquals(
            sale.operator,
            self.user1
        )
        self.assertEquals(
            sale.payment,
            Payment.objects.all()[0]
        )

    def test_product(self):
        spfc = SingleProductFromContainer.objects.all()[0]
        self.assertEquals(
            spfc.quantity,
            1000
        )
        self.assertEquals(
            spfc.sale_price,
            10
        )
        self.assertEquals(
            spfc.container,
            Container.objects.get(pk=1)
        )
        self.assertEquals(
            spfc.sale,
            Sale.objects.get(sender=self.user1)
        )

    def test_balances(self):
        self.assertAlmostEquals(
            self.user1.balance,
            Decimal(110)
        )


class MiscellaneousSaleRechargingWithOperatorTestCase(TestCase):
    fixtures = ['shops.json', 'special_members.json']

    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            balance=100
            )
        self.user2 = User.objects.create(
            username='user2'
            )
        self.cash = Cash.objects.create(
            amount=10,
            sender=self.user1,
            recipient=self.user2
            )
        sale_recharging(
            sender=self.user1,
            operator=self.user2,
            date=date.today(),
            wording='Rechargement manuel',
            payments_list=[self.cash]
        )

    def test_payment(self):
        # Exceptions are directly raised if objects does not exists
        payment = Payment.objects.all()[0]  # Theorically the only one.
        self.assertAlmostEquals(
            payment.amount,
            Decimal(10)
        )
        self.assertCountEqual(
            payment.list_cheque()[0],
            []
        )
        self.assertCountEqual(
            payment.list_lydia()[0],
            []
        )
        self.assertCountEqual(
            payment.list_cash()[0],
            [self.cash]
        )
        self.assertCountEqual(
            payment.list_debit_balance()[0],
            []
        )
        self.assertAlmostEquals(
            payment.list_cheque()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_lydia()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_cash()[1],
            Decimal(10)
        )
        self.assertAlmostEquals(
            payment.list_debit_balance()[1],
            Decimal(0)
        )

    def test_sale(self):
        # Exceptions are directly raised if objects does not exists
        sale = Sale.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            sale.amount,
            Decimal(10)
        )
        self.assertTrue(sale.done)
        self.assertTrue(sale.is_credit)
        self.assertEquals(
            sale.category,
            'recharging'
        )
        self.assertEquals(
            sale.wording,
            'Rechargement manuel'
        )
        self.assertIsNone(sale.justification)
        self.assertEquals(
            sale.sender,
            self.user1
        )
        self.assertEquals(
            sale.recipient,
            User.objects.get(username='AE_ENSAM')
        )
        self.assertEquals(
            sale.operator,
            self.user2
        )
        self.assertEquals(
            sale.payment,
            Payment.objects.all()[0]
        )

    def test_product(self):
        spfc = SingleProductFromContainer.objects.all()[0]
        self.assertEquals(
            spfc.quantity,
            1000
        )
        self.assertEquals(
            spfc.sale_price,
            10
        )
        self.assertEquals(
            spfc.container,
            Container.objects.get(pk=1)
        )
        self.assertEquals(
            spfc.sale,
            Sale.objects.get(sender=self.user1)
        )

    def test_balances(self):
        self.assertAlmostEquals(
            self.user1.balance,
            Decimal(110)
        )


class MiscellaneousSaleExceptionnalCreditTestCase(TestCase):
    fixtures = ['shops.json', 'special_members.json']

    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            balance=100
            )
        self.user2 = User.objects.create(
            username='user2',
            balance=10
            )
        sale_exceptionnal_movement(
            operator=self.user2,
            affected=self.user1,
            is_credit=True,
            amount=10,
            date=date.today(),
            justification='Exception'
        )

    def test_payment(self):
        # Exceptions are directly raised if objects does not exists
        payment = Payment.objects.all()[0]  # Theorically the only one.
        self.assertAlmostEquals(
            payment.amount,
            Decimal(10)
        )
        self.assertCountEqual(
            payment.list_cheque()[0],
            []
        )
        self.assertCountEqual(
            payment.list_lydia()[0],
            []
        )
        self.assertCountEqual(
            payment.list_cash()[0],
            []
        )
        self.assertCountEqual(
            payment.list_debit_balance()[0],
            []
        )
        self.assertAlmostEquals(
            payment.list_cheque()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_lydia()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_cash()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_debit_balance()[1],
            Decimal(0)
        )

    def test_sale(self):
        # Exceptions are directly raised if objects does not exists
        sale = Sale.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            sale.amount,
            Decimal(10)
        )
        self.assertTrue(sale.done)
        self.assertTrue(sale.is_credit)
        self.assertEquals(
            sale.category,
            'exceptionnal_movement'
        )
        self.assertEquals(
            sale.wording,
            'Mouvement exceptionnel'
        )
        self.assertEquals(
            sale.justification,
            'Exception'
        )
        self.assertEquals(
            sale.sender,
            self.user1
        )
        self.assertEquals(
            sale.recipient,
            User.objects.get(username='AE_ENSAM')
        )
        self.assertEquals(
            sale.operator,
            self.user2
        )
        self.assertEquals(
            sale.payment,
            Payment.objects.all()[0]
        )

    def test_product(self):
        spfc = SingleProductFromContainer.objects.all()[0]
        self.assertEquals(
            spfc.quantity,
            1000
        )
        self.assertEquals(
            spfc.sale_price,
            10
        )
        self.assertEquals(
            spfc.container,
            Container.objects.get(pk=1)
        )
        self.assertEquals(
            spfc.sale,
            Sale.objects.get(sender=self.user1)
        )

    def test_balances(self):
        self.assertAlmostEquals(
            self.user1.balance,
            Decimal(110)
        )


class MiscellaneousSaleExceptionnalDebitTestCase(TestCase):
    fixtures = ['shops.json', 'special_members.json']

    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            balance=100
            )
        self.user2 = User.objects.create(
            username='user2',
            balance=10
            )
        sale_exceptionnal_movement(
            operator=self.user2,
            affected=self.user1,
            is_credit=False,
            amount=10,
            date=date.today(),
            justification='Exception'
        )

    def test_debit_balance(self):
        debit_balance = DebitBalance.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            debit_balance.amount,
            Decimal(10)
        )
        self.assertEquals(
            debit_balance.sender,
            self.user1
        )
        self.assertEquals(
            debit_balance.recipient,
            User.objects.get(username='AE_ENSAM')
        )

    def test_payment(self):
        # Exceptions are directly raised if objects does not exists
        payment = Payment.objects.all()[0]  # Theorically the only one.
        self.assertAlmostEquals(
            payment.amount,
            Decimal(10)
        )
        self.assertCountEqual(
            payment.list_cheque()[0],
            []
        )
        self.assertCountEqual(
            payment.list_lydia()[0],
            []
        )
        self.assertCountEqual(
            payment.list_cash()[0],
            []
        )
        self.assertCountEqual(
            payment.list_debit_balance()[0],
            [DebitBalance.objects.all()[0]]
        )
        self.assertAlmostEquals(
            payment.list_cheque()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_lydia()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_cash()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_debit_balance()[1],
            Decimal(10)
        )

    def test_sale(self):
        # Exceptions are directly raised if objects does not exists
        sale = Sale.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            sale.amount,
            Decimal(10)
        )
        self.assertTrue(sale.done)
        self.assertFalse(sale.is_credit)
        self.assertEquals(
            sale.category,
            'exceptionnal_movement'
        )
        self.assertEquals(
            sale.wording,
            'Mouvement exceptionnel'
        )
        self.assertEquals(
            sale.justification,
            'Exception'
        )
        self.assertEquals(
            sale.sender,
            self.user1
        )
        self.assertEquals(
            sale.recipient,
            User.objects.get(username='AE_ENSAM')
        )
        self.assertEquals(
            sale.operator,
            self.user2
        )
        self.assertEquals(
            sale.payment,
            Payment.objects.all()[0]
        )

    def test_product(self):
        spfc = SingleProductFromContainer.objects.all()[0]
        self.assertEquals(
            spfc.quantity,
            1000
        )
        self.assertEquals(
            spfc.sale_price,
            10
        )
        self.assertEquals(
            spfc.container,
            Container.objects.get(pk=1)
        )
        self.assertEquals(
            spfc.sale,
            Sale.objects.get(sender=self.user1)
        )

    def test_balances(self):
        self.assertAlmostEquals(
            self.user1.balance,
            Decimal(90)
        )


class MiscellaneousDirectSaleTestCase(TestCase):
    fixtures = ['shops.json', 'special_members.json']

    def setUp(self):
        self.user1 = User.objects.create(
            username='user1',
            balance=100
            )
        self.shop = Shop.objects.create(
            name='Shop name',
            description='Shop description'
            )
        self.pu1 = ProductUnit.objects.create(
            name='pu1 name',
            description='pu1 description',
            unit='CL',
            type='keg'
            )
        self.pb1 = ProductBase.objects.create(
            name='pb1 name',
            description='pb1 description',
            manual_price=1.15,
            brand='pb1 brand',
            type='single_product',
            shop=self.shop
            )
        self.pb2 = ProductBase.objects.create(
            name='pb2 name',
            description='pb2 description',
            manual_price=150,
            brand='pb2 brand',
            type='container',
            quantity=100,
            product_unit=self.pu1,
            shop=self.shop
            )
        self.sp_pb1 = SingleProduct.objects.create(
            price=1,
            purchase_date='2016-01-01',
            place='place sp',
            product_base=self.pb1,
            sale_price=1,
            is_sold=True
            )
        self.c_pb2 = Container.objects.create(
            price=100,
            purchase_date='2016-01-01',
            place='place sp',
            product_base=self.pb2
            )
        self.spfc_pb2 = SingleProductFromContainer.objects.create(
            quantity=10,
            container=self.c_pb2,
            sale_price=15,
            )
        sale_sale(
            sender=self.user1,
            operator=self.user1,
            date=date.today(),
            wording='Vente Shop name',
            products_list=[self.sp_pb1, self.spfc_pb2]
        )

    def test_debit_balance(self):
        debit_balance = DebitBalance.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            debit_balance.amount,
            Decimal(16)
        )
        self.assertEquals(
            debit_balance.sender,
            self.user1
        )
        self.assertEquals(
            debit_balance.recipient,
            User.objects.get(username='AE_ENSAM')
        )

    def test_payment(self):
        # Exceptions are directly raised if objects does not exists
        payment = Payment.objects.all()[0]  # Theorically the only one.
        self.assertAlmostEquals(
            payment.amount,
            Decimal(16)
        )
        self.assertCountEqual(
            payment.list_cheque()[0],
            []
        )
        self.assertCountEqual(
            payment.list_lydia()[0],
            []
        )
        self.assertCountEqual(
            payment.list_cash()[0],
            []
        )
        self.assertCountEqual(
            payment.list_debit_balance()[0],
            [DebitBalance.objects.all()[0]]
        )
        self.assertAlmostEquals(
            payment.list_cheque()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_lydia()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_cash()[1],
            Decimal(0)
        )
        self.assertAlmostEquals(
            payment.list_debit_balance()[1],
            Decimal(16)
        )

    def test_sale(self):
        # Exceptions are directly raised if objects does not exists
        sale = Sale.objects.get(sender=self.user1)
        self.assertAlmostEquals(
            sale.amount,
            Decimal(16)
        )
        self.assertTrue(sale.done)
        self.assertFalse(sale.is_credit)
        self.assertEquals(
            sale.category,
            'sale'
        )
        self.assertEquals(
            sale.wording,
            'Vente Shop name'
        )
        self.assertIsNone(sale.justification)
        self.assertEquals(
            sale.sender,
            self.user1
        )
        self.assertEquals(
            sale.recipient,
            User.objects.get(username='AE_ENSAM')
        )
        self.assertEquals(
            sale.operator,
            self.user1
        )
        self.assertEquals(
            sale.payment,
            Payment.objects.all()[0]
        )

    def test_products(self):
        self.assertEquals(
            self.sp_pb1.sale,
            Sale.objects.get(sender=self.user1)
        )
        self.assertTrue(self.sp_pb1.is_sold)
        self.assertEquals(
            self.spfc_pb2.sale,
            Sale.objects.get(sender=self.user1)
        )

    def test_balances(self):
        self.assertAlmostEquals(
            self.user1.balance,
            Decimal(84)
        )
