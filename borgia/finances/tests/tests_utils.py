import decimal

from django.test import TestCase
from finances.utils import (calculate_lydia_fee_from_total,
                            calculate_total_amount_lydia)


class CalculationsLydiaTestCase(TestCase):
    def test_calculate_lydia_fee_from_total(self):
        total_amount = 10.00
        base_fee = 0.10
        ratio_fee = 1.0

        fee = calculate_lydia_fee_from_total(
            total_amount, base_fee, ratio_fee)
        expected = decimal.Decimal('0.2')
        self.assertEqual(expected, fee)

        total_amount = 53.00
        base_fee = 0.16
        ratio_fee = 1.3

        fee = calculate_lydia_fee_from_total(
            total_amount, base_fee, ratio_fee)
        expected = decimal.Decimal('0.85')
        self.assertEqual(expected, fee)

    def test_calculate_lydia_fee_from_total_with_tax(self):
        total_amount = 10.00
        base_fee = 0.10
        ratio_fee = 1.0
        tax_fee = 1.3

        fee = calculate_lydia_fee_from_total(
            total_amount, base_fee, ratio_fee, tax_fee)
        expected = decimal.Decimal('0.26')
        self.assertEqual(expected, fee)

        total_amount = 53.00
        base_fee = 0.16
        ratio_fee = 1.3
        tax_fee = 1.65

        fee = calculate_lydia_fee_from_total(
            total_amount, base_fee, ratio_fee, tax_fee)
        expected = decimal.Decimal('1.41')
        self.assertEqual(expected, fee)

    def test_calculate_total_amount_lydia(self):
        recharging_amount = 9.8
        base_fee = 0.10
        ratio_fee = 1.0

        total = calculate_total_amount_lydia(
            recharging_amount, base_fee, ratio_fee)
        expected = decimal.Decimal('10.00')
        self.assertEqual(expected, total)

        recharging_amount = 52.15
        base_fee = 0.16
        ratio_fee = 1.3

        total = calculate_total_amount_lydia(
            recharging_amount, base_fee, ratio_fee)
        expected = decimal.Decimal('53.00')
        self.assertEqual(expected, total)

    def test_calculate_total_amount_lydia_with_tax(self):
        recharging_amount = 9.74
        base_fee = 0.10
        ratio_fee = 1.0
        tax_fee = 1.3

        total = calculate_total_amount_lydia(
            recharging_amount, base_fee, ratio_fee, tax_fee)
        expected = decimal.Decimal('10.00')
        self.assertEqual(expected, total)

        recharging_amount = 51.59
        base_fee = 0.16
        ratio_fee = 1.3
        tax_fee = 1.65

        total = calculate_total_amount_lydia(
            recharging_amount, base_fee, ratio_fee, tax_fee)
        expected = decimal.Decimal('53.00')
        self.assertEqual(expected, total)
