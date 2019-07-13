from borgia.tests.tests_views import BaseBorgiaViewsTestCase
from shops.models import Product, Shop


class BaseShopTestCase(BaseBorgiaViewsTestCase):
    def setUp(self):
        self.shop1 = Shop.objects.create(
            name='Shop1 name',
            description='Shop1 description')
        self.shop2 = Shop.objects.create(
            name='lowercase name',
            description='Shop2 description'
        )


class ShopTestCase(BaseShopTestCase):
    def test_str(self):
        self.assertEqual(self.shop1.__str__(), 'Shop1 name')
        self.assertEqual(self.shop2.__str__(), 'Lowercase name')


class ProductTestCase(BaseShopTestCase):
    def setUp(self):
        super().setUp()
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

    def test_str(self):
        self.assertEqual(self.product1.__str__(), 'Product1 name')
        self.assertEqual(self.product2.__str__(), 'Product2 name')
        self.assertEqual(self.product3.__str__(), 'product3 name')
        self.assertEqual(self.product4.__str__(),
                         'A different product for a different shop')

    def test_get_unit_display(self):
        self.assertEqual(self.product1.get_unit_display(), 'cl')
        self.assertEqual(self.product2.get_unit_display(), 'g')
        self.assertEqual(self.product3.get_unit_display(), 'unit')
        self.assertEqual(self.product4.get_unit_display(), 'unit')

    def test_get_upper_unit_display(self):
        self.assertEqual(self.product1.get_upper_unit_display(), 'L')
        self.assertEqual(self.product2.get_upper_unit_display(), 'Kg')
        self.assertEqual(self.product3.get_upper_unit_display(), 'Unit')
        self.assertEqual(self.product4.get_upper_unit_display(), 'Unit')
