import decimal

from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from shops.models import Product, Shop
from stocks.models import (Inventory, InventoryProduct, StockEntry,
                           StockEntryProduct)


class BaseStocksTestCase(BaseBorgiaViewsTestCase):
    def setUp(self):
        super().setUp()

        ### SHOP ###
        self.shop1 = Shop.objects.create(
            name='Shop1 name',
            description='Shop1 description')
        self.shop2 = Shop.objects.create(
            name='lowercase name',
            description='Shop2 description'
        )
        self.product1 = Product.objects.create(
            name='Product1 name',
            unit='CL',
            shop=self.shop1
        )
        self.product2 = Product.objects.create(
            name='Product2 name',
            unit='G',
            shop=self.shop1,
            is_manual=True
        )
        self.product3 = Product.objects.create(
            name='product3 name',
            shop=self.shop1
        )
        self.product4 = Product.objects.create(
            name='A different product for a different shop',
            shop=self.shop2
        )

        ### STOCKENTRY ###
        self.stockentry1 = StockEntry.objects.create(
            operator=self.user1,
            shop=self.shop1
        )
        self.stockentry2 = StockEntry.objects.create(
            operator=self.user1,
            shop=self.shop2
        )

        self.stockentry1_product1 = StockEntryProduct.objects.create(
            stockentry=self.stockentry1,
            product=self.product1,
            quantity=3,
            price=decimal.Decimal('1.0')
        )
        self.stockentry1_product2 = StockEntryProduct.objects.create(
            stockentry=self.stockentry1,
            product=self.product2,
            quantity=7,
            price=decimal.Decimal('2.0')
        )
        self.stockentry1_product3 = StockEntryProduct.objects.create(
            stockentry=self.stockentry1,
            product=self.product3,
            quantity=12,
            price=decimal.Decimal('4.0')
        )

        self.stockentry2_product1 = StockEntryProduct.objects.create(
            stockentry=self.stockentry2,
            product=self.product4,
            quantity=20,
            price=decimal.Decimal('5.0')
        )


class StockEntryTestCase(BaseStocksTestCase):
    def test_total(self):
        total = self.stockentry1.total()
        self.assertEqual(total, decimal.Decimal('7.0'))

        total = self.stockentry2.total()
        self.assertEqual(total, decimal.Decimal('5.0'))
