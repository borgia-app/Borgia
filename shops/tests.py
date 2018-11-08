# import random
# import unittest
# import decimal

# from django.test import TestCase

# from settings_data.models import Setting
# from shops.models import *

# class ShopTestCase(TestCase):
#     def setUp(self):
#         self.shop = Shop.objects.create(
#             name='Shop name',
#             description='Shop description'
#         )
#         self.pu1 = ProductUnit.objects.create(
#             name='pu1 name',
#             description='pu1 description',
#             unit='CL',
#             type='keg'
#         )
#         self.pu2 = ProductUnit.objects.create(
#             name='pu2 name',
#             description='pu2 description',
#             unit='G',
#             type='meat'
#         )
#         self.pb1 = ProductBase.objects.create(
#             name='pb1 name',
#             description='pb1 description',
#             manual_price=1.15,
#             brand='pb1 brand',
#             type='single_product',
#             shop=self.shop
#         )
#         self.pb2 = ProductBase.objects.create(
#             name='pb2 name',
#             description='pb2 description',
#             manual_price=150,
#             brand='pb2 brand',
#             type='container',
#             quantity=100,
#             product_unit=self.pu1,
#             shop=self.shop
#         )
#         self.pb3 = ProductBase.objects.create(
#             name='pb3 name',
#             description='pb3 description',
#             manual_price=150,
#             brand='pb3 brand',
#             type='container',
#             quantity=100,
#             product_unit=self.pu2,
#             shop=self.shop
#         )
#         self.pb4 = ProductBase.objects.create(
#             name='pb4 name',
#             description='pb4 description shooter',
#             manual_price=1.15,
#             brand='pb4 brand',
#             type='single_product',
#             shop=self.shop
#         )
#         # 10 instances of pb1, prices from 1 to 1.10
#         # 5 sold, 5 unsold
#         self.sp_pb1 = []
#         for i in range(0, 5):
#             self.sp_pb1.append(SingleProduct.objects.create(
#                 price=1+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb1
#                 ))
#         for i in range(5, 10):
#             self.sp_pb1.append(SingleProduct.objects.create(
#                 price=1+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb1,
#                 is_sold=True
#                 ))
#         # 10 instances of pb2, prices from 100 to 110
#         # 5 sold, 5 unsold
#         self.c_pb2 = []
#         for i in range(0, 5):
#             self.c_pb2.append(Container.objects.create(
#                 price=100+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb2))
#         for i in range(5, 10):
#             self.c_pb2.append(Container.objects.create(
#                 price=100+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb2,
#                 is_sold=True))
#         # 10 instances of pb3, prices from 100 to 110
#         # 5 sold, 5 unsold
#         self.c_pb3 = []
#         for i in range(0, 5):
#             self.c_pb3.append(Container.objects.create(
#                 price=100+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb3))
#         for i in range(5, 10):
#             self.c_pb3.append(Container.objects.create(
#                 price=100+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb3,
#                 is_sold=True))
#         # 10 instances of pb4, prices from 1 to 1.10
#         # 5 sold, 5 unsold
#         self.sp_pb4 = []
#         for i in range(0, 5):
#             self.sp_pb4.append(SingleProduct.objects.create(
#                 price=1+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb4
#                 ))
#         for i in range(5, 10):
#             self.sp_pb4.append(SingleProduct.objects.create(
#                 price=1+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb4,
#                 is_sold=True
#                 ))
#
#     def test_str(self):
#         self.assertEqual(self.shop.__str__(), 'Shop name')
#
#     def test_list_product_base_single_product(self):
#         """
#         :note: Some issues when testing list of tuples directly, let's test
#         elements directly.
#         """
#         # status_sold = False
#         self.assertEqual(
#             self.shop.list_product_base_single_product(
#                 status_sold=False)[0][0],
#             self.pb1)
#         self.assertCountEqual(
#             self.shop.list_product_base_single_product(
#                 status_sold=False)[0][1],
#             [self.sp_pb1[i] for i in range(0, 5)])
#         self.assertEqual(
#             len(self.shop.list_product_base_single_product(
#                 status_sold=False)),
#             1
#         )
#         # status_sold = True
#         self.assertEqual(
#             self.shop.list_product_base_single_product(
#                 status_sold=True)[0][0],
#             self.pb1)
#         self.assertCountEqual(
#             self.shop.list_product_base_single_product(
#                 status_sold=True)[0][1],
#             [self.sp_pb1[i] for i in range(5, 10)])
#         self.assertEqual(
#             len(self.shop.list_product_base_single_product(
#                 status_sold=True)),
#             1
#         )
#         # status_sold = 'both'
#         self.assertEqual(
#             self.shop.list_product_base_single_product(
#                 status_sold='both')[0][0],
#             self.pb1)
#         self.assertCountEqual(
#             self.shop.list_product_base_single_product(
#                 status_sold='both')[0][1],
#             [self.sp_pb1[i] for i in range(0, 10)])
#         self.assertEqual(
#             len(self.shop.list_product_base_single_product(
#                 status_sold='both')),
#             1
#         )
#
#     def test_list_product_base_single_product_shooter(self):
#         """
#         :note: Some issues when testing list of tuples directly, let's test
#         elements directly.
#         """
#         # status_sold = False
#         self.assertEqual(
#             self.shop.list_product_base_single_product_shooter(
#                 status_sold=False)[0][0],
#             self.pb4)
#         self.assertCountEqual(
#             self.shop.list_product_base_single_product_shooter(
#                 status_sold=False)[0][1],
#             [self.sp_pb4[i] for i in range(0, 5)])
#         self.assertEqual(
#             len(self.shop.list_product_base_single_product_shooter(
#                 status_sold=False)),
#             1
#         )
#         # status_sold = True
#         self.assertEqual(
#             self.shop.list_product_base_single_product_shooter(
#                 status_sold=True)[0][0],
#             self.pb4)
#         self.assertCountEqual(
#             self.shop.list_product_base_single_product_shooter(
#                 status_sold=True)[0][1],
#             [self.sp_pb4[i] for i in range(5, 10)])
#         self.assertEqual(
#             len(self.shop.list_product_base_single_product_shooter(
#                 status_sold=True)),
#             1
#         )
#         # status_sold = 'both'
#         self.assertEqual(
#             self.shop.list_product_base_single_product_shooter(
#                 status_sold='both')[0][0],
#             self.pb4)
#         self.assertCountEqual(
#             self.shop.list_product_base_single_product_shooter(
#                 status_sold='both')[0][1],
#             [self.sp_pb4[i] for i in range(0, 10)])
#         self.assertEqual(
#             len(self.shop.list_product_base_single_product_shooter(
#                 status_sold='both')),
#             1
#         )
#
#     def test_list_product_base_container(self):
#         """
#         :note: Some issues when testing list of tuples directly, let's test
#         elements directly.
#         """
#         # Type 'keg'
#         self.assertEqual(
#             self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold=False)[0][0],
#             self.pb2)
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold=False)[0][1],
#             [self.c_pb2[i] for i in range(0, 5)])
#         self.assertEqual(
#             len(self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold=True)),
#             1
#         )
#         self.assertEqual(
#             self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold=True)[0][0],
#             self.pb2)
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold=True)[0][1],
#             [self.c_pb2[i] for i in range(5, 10)])
#         self.assertEqual(
#             len(self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold='both')),
#             1
#         )
#         self.assertEqual(
#             self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold='both')[0][0],
#             self.pb2)
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold='both')[0][1],
#             [self.c_pb2[i] for i in range(0, 10)])
#         self.assertEqual(
#             len(self.shop.list_product_base_container(
#                 type='keg',
#                 status_sold=False)),
#             1
#         )
#         # Type 'meat'
#         self.assertEqual(
#             self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold=False)[0][0],
#             self.pb3)
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold=False)[0][1],
#             [self.c_pb3[i] for i in range(0, 5)])
#         self.assertEqual(
#             len(self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold=False)),
#             1
#         )
#         self.assertEqual(
#             self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold=True)[0][0],
#             self.pb3)
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold=True)[0][1],
#             [self.c_pb3[i] for i in range(5, 10)])
#         self.assertEqual(
#             len(self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold=True)),
#             1
#         )
#         self.assertEqual(
#             self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold='both')[0][0],
#             self.pb3)
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold='both')[0][1],
#             [self.c_pb3[i] for i in range(0, 10)])
#         self.assertEqual(
#             len(self.shop.list_product_base_container(
#                 type='meat',
#                 status_sold='both')),
#             1
#         )
#         # Type unset
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='unset',
#                 status_sold=False),
#             [])
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='unset',
#                 status_sold=False),
#             [])
#         self.assertCountEqual(
#             self.shop.list_product_base_container(
#                 type='unset',
#                 status_sold='both'),
#             [])
#
#
# class ProductBaseTestCase(TestCase):
#     def setUp(self):
#         self.shop = Shop.objects.create(
#             name='Shop name',
#             description='Shop description'
#         )
#         self.pu1 = ProductUnit.objects.create(
#             name='pu1 name',
#             description='pu1 description',
#             unit='CL',
#             type='keg'
#         )
#         self.pu2 = ProductUnit.objects.create(
#             name='pu2 name',
#             description='pu2 description',
#             unit='G',
#             type='meat'
#         )
#         self.pb1 = ProductBase.objects.create(
#             name='pb1 name',
#             description='pb1 description',
#             manual_price=1.15,
#             brand='pb1 brand',
#             type='single_product',
#             shop=self.shop
#         )
#         self.pb2 = ProductBase.objects.create(
#             name='pb2 name',
#             description='pb2 description',
#             manual_price=150,
#             brand='pb2 brand',
#             type='container',
#             quantity=100,
#             product_unit=self.pu1,
#             shop=self.shop
#         )
#         self.pb3 = ProductBase.objects.create(
#             name='pb3 name',
#             description='pb3 description',
#             manual_price=150,
#             brand='pb3 brand',
#             type='container',
#             quantity=100,
#             product_unit=self.pu2,
#             shop=self.shop,
#             is_manual=True
#         )
#         self.pb4 = ProductBase.objects.create(
#             name='pb4 name',
#             description='pb4 description shooter',
#             manual_price=1.15,
#             brand='pb4 brand',
#             type='single_product',
#             shop=self.shop,
#             is_manual=True
#         )
#         self.pb5 = ProductBase.objects.create(
#             name='pb5 name',
#             description='pb5 description',
#             manual_price=1.15,
#             brand='pb5 brand',
#             type='single_product',
#             shop=self.shop,
#             is_manual=True
#         )
#         # 10 instances of pb1, prices from 1 to 1.10
#         # 5 sold, 5 unsold
#         self.sp_pb1 = []
#         for i in range(0, 5):
#             self.sp_pb1.append(SingleProduct.objects.create(
#                 price=1+i*0.1,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb1
#                 ))
#         for i in range(5, 10):
#             self.sp_pb1.append(SingleProduct.objects.create(
#                 price=1+i*0.1,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb1,
#                 is_sold=True
#                 ))
#         # 10 instances of pb2, prices from 100 to 110
#         # 5 sold, 5 unsold
#         self.c_pb2 = []
#         for i in range(0, 5):
#             self.c_pb2.append(Container.objects.create(
#                 price=100+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb2))
#         for i in range(5, 10):
#             self.c_pb2.append(Container.objects.create(
#                 price=100+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb2,
#                 is_sold=True))
#         # 10 instances of pb3, prices from 100 to 110
#         # 5 sold, 5 unsold
#         self.c_pb3 = []
#         for i in range(0, 5):
#             self.c_pb3.append(Container.objects.create(
#                 price=100+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb3))
#         for i in range(5, 10):
#             self.c_pb3.append(Container.objects.create(
#                 price=100+i,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb3,
#                 is_sold=True))
#         # 10 instances of pb4, prices from 1 to 1.10
#         # 5 sold, 5 unsold
#         self.sp_pb4 = []
#         for i in range(0, 5):
#             self.sp_pb4.append(SingleProduct.objects.create(
#                 price=1+i*0.2,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb4
#                 ))
#         for i in range(5, 10):
#             self.sp_pb4.append(SingleProduct.objects.create(
#                 price=1+i*0.2,
#                 purchase_date='2016-01-01',
#                 place='place sp',
#                 product_base=self.pb4,
#                 is_sold=True
#                 ))
#
#     def test_str(self):
#         self.assertEqual(
#             self.pb1.__str__(),
#             self.pb1.name)
#         self.assertEqual(
#             self.pb2.__str__(),
#             (self.pb2.name
#              + ' '
#              + str(self.pb2.quantity)
#              + ' '
#              + self.pb2.product_unit.unit))
#
#     def test_set_calculated_price_mean(self):
#         # Without margin profit, just mean
#         # ProductBase1:
#         # not sold: sp_pb1[0, 1, 2, 3, 4]
#         # Mean = (1 + 1.1 + 1.2 + 1.3 + 1.4)/5 = 1.2
#         self.assertAlmostEqual(
#             self.pb1.set_calculated_price_mean(),
#             decimal.Decimal(1.20)
#         )
#         self.assertAlmostEqual(
#             self.pb2.set_calculated_price_mean(),
#             decimal.Decimal(102)
#         )
#         # With margin profit, 10%
#         # ProductBase1:
#         # not sold: sp_pb1[0, 1, 2, 3, 4]
#         # Mean = (1 + 1.1 + 1.2 + 1.3 + 1.4)/5 = 1.2
#         # must be 1.2*(1+10/100) = 1.32
#         Setting.objects.create(
#             name='MARGIN_PROFIT',
#             description='margin profit',
#             value='10',
#             value_type='f'
#         )
#         self.assertAlmostEqual(
#             self.pb1.set_calculated_price_mean(),
#             decimal.Decimal(1.32)
#         )
#         self.assertAlmostEqual(
#             self.pb2.set_calculated_price_mean(),
#             decimal.Decimal(112.2)
#         )
#         # With margin profit, random int %
#         r = random.randint(0, 100)
#         s = Setting.objects.get(name='MARGIN_PROFIT')
#         s.value = r
#         s.save()
#         self.assertAlmostEqual(
#             self.pb1.set_calculated_price_mean(),
#             decimal.Decimal(round(1.2*(1+r/100), 2))
#         )
#         self.assertAlmostEqual(
#             self.pb2.set_calculated_price_mean(),
#             decimal.Decimal(round(102*(1+r/100), 2))
#         )
#         s.delete()
#
#         self.assertEqual(
#             self.pb5.set_calculated_price_mean(),
#             0
#         )
#
#     def test_calculated_price_usual(self):
#         """
#         :note:: I use directly set_calculated_price_mean here. I assume their
#         tests passed well.
#         """
#         # ProductBase1: directly the mean (single_product)
#         self.assertAlmostEqual(
#             self.pb1.calculated_price_usual(),
#             self.pb1.set_calculated_price_mean()
#         )
#         # ProductBase2: with the quantity
#         self.assertAlmostEqual(
#             self.pb2.calculated_price_usual(),
#             ((self.pu1.usual_quantity() * self.pb2.set_calculated_price_mean())
#              / self.pb2.quantity)
#         )
#
#         self.assertEqual(
#             self.pb5.set_calculated_price_mean(),
#             0
#         )
#
#     def test_manual_price_usual(self):
#         # ProductBase1: directly the manual price (single_product)
#         self.assertAlmostEqual(
#             self.pb1.manual_price_usual(),
#             self.pb1.manual_price
#         )
#         # ProductBase2: with the quantity
#         self.assertAlmostEqual(
#             self.pb2.manual_price_usual(),
#             ((self.pu1.usual_quantity() * self.pb2.manual_price)
#              / self.pb2.quantity)
#         )
#
#     def test_get_moded_price(self):
#         """
#         :note:: I use directly set_calculated_price_mean here. I assume their
#         tests passed well.
#         """
#         self.assertAlmostEqual(
#             self.pb1.get_moded_price(),
#             self.pb1.set_calculated_price_mean()
#         )
#         self.assertAlmostEqual(
#             self.pb2.get_moded_price(),
#             self.pb2.set_calculated_price_mean()
#         )
#         self.assertAlmostEqual(
#             self.pb3.get_moded_price(),
#             self.pb3.manual_price
#         )
#         self.assertAlmostEqual(
#             self.pb4.get_moded_price(),
#             self.pb4.manual_price
#         )
#
#     def test_get_moded_usual_price(self):
#         """
#         :note:: I use directly calculated_price_usual here. I assume their
#         tests passed well. Same for manual_price_usual method.
#         """
#         self.assertAlmostEqual(
#             self.pb1.get_moded_usual_price(),
#             self.pb1.calculated_price_usual()
#         )
#         self.assertAlmostEqual(
#             self.pb2.get_moded_usual_price(),
#             self.pb2.calculated_price_usual()
#         )
#         self.assertAlmostEqual(
#             self.pb3.get_moded_usual_price(),
#             self.pb3.manual_price_usual()
#         )
#         self.assertAlmostEqual(
#             self.pb4.get_moded_usual_price(),
#             self.pb4.manual_price_usual()
#         )
#
#     def test_deviating_price_from_auto(self):
#         # ProductBase1
#         # price auto = 1.2
#         # manual price = 1.15
#         # deviating = ((1.2-1.15)/1.2)*100 (%) = 4.17%
#         self.assertAlmostEqual(
#             self.pb1.deviating_price_from_auto(),
#             decimal.Decimal(4.17)
#         )
#         # ProductBase2
#         # price auto = 102
#         # manual price = 150
#         # deviating = ((102-150)/102)*100 (%) = 47.06%
#         self.assertAlmostEqual(
#             self.pb2.deviating_price_from_auto(),
#             decimal.Decimal(47.06)
#         )
#
#         self.assertEqual(
#             self.pb5.deviating_price_from_auto(),
#             None
#         )
#
#     def test_quantity_products_stock(self):
#         self.assertEqual(
#             self.pb1.quantity_products_stock(),
#             5
#         )
#         self.assertEqual(
#             self.pb2.quantity_products_stock(),
#             5
#         )
#         self.assertEqual(
#             self.pb3.quantity_products_stock(),
#             5
#         )
#         self.assertEqual(
#             self.pb4.quantity_products_stock(),
#             5
#         )
#         self.assertEqual(
#             self.pb5.quantity_products_stock(),
#             0
#         )
#
#
# class ProductUnitTestCase(TestCase):
#     def setUp(self):
#         self.pu1 = ProductUnit.objects.create(
#             name='pu1 name',
#             description='pu1 description',
#             unit='CL',
#             type='keg'
#         )
#         self.pu2 = ProductUnit.objects.create(
#             name='pu2 name',
#             description='pu2 description',
#             unit='G',
#             type='liquor'
#         )
#         self.pu3 = ProductUnit.objects.create(
#             name='pu3 name',
#             description='pu3 description',
#             unit='G',
#             type='syrup'
#         )
#         self.pu4 = ProductUnit.objects.create(
#             name='pu4 name',
#             description='pu4 description',
#             unit='G',
#             type='soft'
#         )
#         self.pu5 = ProductUnit.objects.create(
#             name='pu5 name',
#             description='pu5 description',
#             unit='G',
#             type='food'
#         )
#         self.pu6 = ProductUnit.objects.create(
#             name='pu6 name',
#             description='pu6 description',
#             unit='G',
#             type='meat'
#         )
#         self.pu7 = ProductUnit.objects.create(
#             name='pu7 name',
#             description='pu7 description',
#             unit='G',
#             type='cheese'
#         )
#         self.pu8 = ProductUnit.objects.create(
#             name='pu8 name',
#             description='pu8 description',
#             unit='G',
#             type='side'
#         )
#         self.pu9 = ProductUnit.objects.create(
#             name='pu9 name',
#             description='pu9 description',
#             unit='G',
#             type='fictional_money'
#         )
#
#     def test_str(self):
#         self.assertEqual(
#             self.pu1.__str__(),
#             'pu1 name'
#         )
#
#     def test_usual_quantity(self):
#         self.assertEqual(
#             self.pu1.usual_quantity(),
#             25
#         )
#         self.assertEqual(
#             self.pu2.usual_quantity(),
#             4
#         )
#         self.assertEqual(
#             self.pu3.usual_quantity(),
#             4
#         )
#         self.assertEqual(
#             self.pu4.usual_quantity(),
#             25
#         )
#         self.assertEqual(
#             self.pu5.usual_quantity(),
#             1
#         )
#         self.assertEqual(
#             self.pu6.usual_quantity(),
#             1
#         )
#         self.assertEqual(
#             self.pu7.usual_quantity(),
#             1
#         )
#         self.assertEqual(
#             self.pu8.usual_quantity(),
#             1
#         )
#         self.assertEqual(
#             self.pu9.usual_quantity(),
#             1
#         )
#
#
# class SingleProductTestCase(TestCase):
#     def setUp(self):
#         self.shop = Shop.objects.create(
#             name='Shop name',
#             description='Shop description'
#         )
#         self.pb1 = ProductBase.objects.create(
#             name='pb1 name',
#             description='pb1 description',
#             manual_price=1.15,
#             brand='pb1 brand',
#             type='single_product',
#             shop=self.shop
#         )
#         self.sp_pb1 = SingleProduct.objects.create(
#             price=1,
#             purchase_date='2016-01-01',
#             place='place sp',
#             product_base=self.pb1
#         )
#
#     def test_str(self):
#         self.assertEqual(
#             self.sp_pb1.__str__(),
#             self.pb1.__str__() + ' n°' + str(self.sp_pb1.pk)
#         )
#
#
# class ContainertestCase(TestCase):
#     def setUp(self):
#         self.shop = Shop.objects.create(
#             name='Shop name',
#             description='Shop description'
#         )
#         self.pu1 = ProductUnit.objects.create(
#             name='pu1 name',
#             description='pu1 description',
#             unit='CL',
#             type='keg'
#         )
#         self.pb2 = ProductBase.objects.create(
#             name='pb2 name',
#             description='pb2 description',
#             manual_price=150,
#             brand='pb2 brand',
#             type='container',
#             quantity=150,
#             product_unit=self.pu1,
#             shop=self.shop
#         )
#         self.c1_pb2 = Container.objects.create(
#             price=100,
#             purchase_date='2016-01-01',
#             place='place sp',
#             product_base=self.pb2
#         )
#         self.c2_pb2 = Container.objects.create(
#             price=200,
#             purchase_date='2016-01-01',
#             place='place sp',
#             product_base=self.pb2
#         )
#         self.spfc1_c_pb2 = SingleProductFromContainer.objects.create(
#             quantity=10,
#             sale_price=1,
#             container=self.c1_pb2
#         )
#         self.spfc2_c_pb2 = SingleProductFromContainer.objects.create(
#             quantity=30,
#             sale_price=3,
#             container=self.c1_pb2
#         )
#
#     def test_str(self):
#         self.assertEqual(
#             self.c1_pb2.__str__(),
#             self.pb2.__str__() + ' n°' + str(self.c1_pb2.pk)
#         )
#
#     def test_quantity_sold(self):
#         self.assertAlmostEqual(
#             self.c1_pb2.quantity_sold(),
#             decimal.Decimal(40)
#         )
#         self.assertAlmostEqual(
#             self.c2_pb2.quantity_sold(),
#             decimal.Decimal(0)
#         )
#
#     def test_estimated_quantity_remaining(self):
#         self.assertAlmostEqual(
#             self.c1_pb2.estimated_quantity_remaining()[0],
#             decimal.Decimal(110)
#         )
#         self.assertAlmostEqual(
#             self.c2_pb2.estimated_quantity_remaining()[0],
#             decimal.Decimal(150)
#         )
#         # 110 of 150 = 73.33%
#         self.assertAlmostEqual(
#             self.c1_pb2.estimated_quantity_remaining()[1],
#             decimal.Decimal(73.33)
#         )
#         # 150 of 150 = 100%
#         self.assertAlmostEqual(
#             self.c2_pb2.estimated_quantity_remaining()[1],
#             decimal.Decimal(100)
#         )
#
#
# class SingleProductFromContainertestCase(TestCase):
#     def setUp(self):
#         self.shop = Shop.objects.create(
#             name='Shop name',
#             description='Shop description'
#         )
#         self.pu1 = ProductUnit.objects.create(
#             name='pu1 name',
#             description='pu1 description',
#             unit='CL',
#             type='keg'
#         )
#         self.pb2 = ProductBase.objects.create(
#             name='pb2 name',
#             description='pb2 description',
#             manual_price=150,
#             brand='pb2 brand',
#             type='container',
#             quantity=150,
#             product_unit=self.pu1,
#             shop=self.shop
#         )
#         self.c_pb2 = Container.objects.create(
#             price=100,
#             purchase_date='2016-01-01',
#             place='place sp',
#             product_base=self.pb2
#         )
#         self.spfc_c_pb2 = SingleProductFromContainer.objects.create(
#             quantity=10,
#             sale_price=1,
#             container=self.c_pb2
#         )
#
#     def test_str(self):
#         self.assertEqual(
#             self.spfc_c_pb2.__str__(),
#             (self.pu1.__str__()
#              + ' '
#              + str(self.spfc_c_pb2.quantity)
#              + ' '
#              + self.pu1.get_unit_display())
#         )
