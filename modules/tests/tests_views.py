from django.test import Client
from django.urls import reverse

from modules.models import Category, SelfSaleModule, OperatorSaleModule
from shops.tests.tests_views import BaseShopsViewsTest


class BaseShopModuleViewsTest(BaseShopsViewsTest):
    def setUp(self):
        super().setUp()
        self.selfsalemodule1 = SelfSaleModule.objects.create(
            shop=self.shop1
        )
        self.operatorsalemodule1 = OperatorSaleModule.objects.create(
            shop=self.shop1
        )

class BaseGeneralShopModuleViewsTest(BaseShopModuleViewsTest):
    url_view = None

    def get_url_self_sales(self, shop_pk):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk, 'module_class': 'self_sales'})

    def get_url_operator_sales(self, shop_pk):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk, 'module_class': 'operator_sales'})

    def offline_user_redirection(self):
        """
        Test offline user redirection to login page
        """
        response_offline_user_self_sales = Client().get(
            self.get_url_self_sales(self.shop1.pk))
        response_offline_user_operator_sales = Client().get(
            self.get_url_operator_sales(self.shop1.pk))
        self.assertEqual(response_offline_user_self_sales.status_code, 302)
        self.assertRedirects(response_offline_user_self_sales, '/auth/login/')
        self.assertEqual(response_offline_user_operator_sales.status_code, 302)
        self.assertRedirects(
            response_offline_user_operator_sales, '/auth/login/')


class ShopModuleSaleViewTests(BaseGeneralShopModuleViewsTest):
    url_view = 'url_shop_module_sale'

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopModuleConfigViewTests(BaseGeneralShopModuleViewsTest):
    url_view = 'url_shop_module_config'

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopModuleConfigUpdateViewTests(BaseGeneralShopModuleViewsTest):
    url_view = 'url_shop_module_config_update'

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopModuleCategoryCreateViewTests(BaseGeneralShopModuleViewsTest):
    url_view = 'url_shop_module_category_create'

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class BaseShopModuleCategoryViewsTest(BaseShopModuleViewsTest):
    def setUp(self):
        super().setUp()
        self.category1 = Category.objects.create(
            name='SelfSaleCategory1',
            module=self.selfsalemodule1
        )
        self.category2 = Category.objects.create(
            name='OperatorSaleCategory2',
            module=self.operatorsalemodule1
        )


class BaseFocusShopModuleCategoryViewsTest(BaseShopModuleCategoryViewsTest):
    url_view = None

    def get_url_self_sales(self, shop_pk, category_pk):
        return reverse(self.url_view, 
            kwargs={'shop_pk': shop_pk, 'module_class': 'self_sales', 'category_pk': category_pk})

    def get_url_operator_sales(self, shop_pk, category_pk):
        return reverse(self.url_view, 
            kwargs={'shop_pk': shop_pk, 'module_class': 'operator_sales', 'category_pk': category_pk})

    def offline_user_redirection(self):
        """
        Test offline user redirection to login page
        """
        response_offline_user_self_sales = Client().get(
            self.get_url_self_sales(self.shop1.pk, self.category1.pk))
        response_offline_user_operator_sales = Client().get(
            self.get_url_operator_sales(self.shop1.pk, self.category2.pk))
        self.assertEqual(response_offline_user_self_sales.status_code, 302)
        self.assertRedirects(response_offline_user_self_sales, '/auth/login/')
        self.assertEqual(response_offline_user_operator_sales.status_code, 302)
        self.assertRedirects(
            response_offline_user_operator_sales, '/auth/login/')


class ShopModuleCategoryUpdateViewTests(BaseFocusShopModuleCategoryViewsTest):
    url_view = 'url_shop_module_category_update'

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopModuleCategoryDeleteViewTests(BaseFocusShopModuleCategoryViewsTest):
    url_view = 'url_shop_module_category_delete'

    def test_offline_user_redirection(self):
        super().offline_user_redirection()
