from django.test import Client
from django.urls import reverse

from borgia.tests.utils import get_login_url_redirected
from modules.models import Category, OperatorSaleModule, SelfSaleModule
from shops.tests.tests_views import BaseShopsViewsTest


class BaseShopModuleViewsTest(BaseShopsViewsTest):
    def setUp(self):
        super().setUp()
        self.selfsalemodule1 = SelfSaleModule.objects.create(
            shop=self.shop1,
            state=True
        )
        self.operatorsalemodule1 = OperatorSaleModule.objects.create(
            shop=self.shop1,
            state=True
        )

class BaseGeneralShopModuleViewsTest(BaseShopModuleViewsTest):
    url_view = None

    def get_url(self, shop_pk, module_class):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk, 'module_class': module_class})

    def chief_get(self):
        response_client3_selfsales = self.client3.get(self.get_url(self.shop1.pk, 'self_sales'))
        self.assertEqual(response_client3_selfsales.status_code, 200)
        response_client3_operatorsales = self.client3.get(self.get_url(self.shop1.pk, 'operator_sales'))
        self.assertEqual(response_client3_operatorsales.status_code, 200)

    def not_allowed_user_get(self):
        response_client2_selfsales = self.client2.get(self.get_url(self.shop1.pk, 'self_sales'))
        self.assertEqual(response_client2_selfsales.status_code, 403)
        response_client2_operatorsales = self.client2.get(self.get_url(self.shop1.pk, 'operator_sales'))
        self.assertEqual(response_client2_operatorsales.status_code, 403)

    def not_existing_shop_get(self):
        response_client3 = self.client3.get(self.get_url('5353', 'operator_sales'))
        self.assertEqual(response_client3.status_code, 404)

    def not_existing_module_get(self):
        response_client3 = self.client3.get(self.get_url(self.shop1.pk, 'NE_module'))
        self.assertEqual(response_client3.status_code, 404)

    def offline_user_redirection(self):
        """
        Test offline user redirection to login page
        """
        response_offline_user_selfsales = Client().get(
            self.get_url(self.shop1.pk, 'self_sales'))
        response_offline_user_operatorsales = Client().get(
            self.get_url(self.shop1.pk, 'operator_sales'))
        self.assertEqual(response_offline_user_selfsales.status_code, 302)
        self.assertRedirects(response_offline_user_selfsales, get_login_url_redirected(self.get_url(self.shop1.pk, 'self_sales')))
        self.assertEqual(response_offline_user_operatorsales.status_code, 302)
        self.assertRedirects(
            response_offline_user_operatorsales, get_login_url_redirected(self.get_url(self.shop1.pk, 'operator_sales')))


class ShopModuleSaleViewTests(BaseGeneralShopModuleViewsTest):
    url_view = 'url_shop_module_sale'

    def test_chief_get(self):
        response_client3 = self.client3.get(self.get_url(self.shop1.pk, 'operator_sales'))
        self.assertEqual(response_client3.status_code, 200)

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_existing_module_get(self):
        super().not_existing_module_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopModuleConfigViewTests(BaseGeneralShopModuleViewsTest):
    url_view = 'url_shop_module_config'

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_existing_module_get(self):
        super().not_existing_module_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopModuleConfigUpdateViewTests(BaseGeneralShopModuleViewsTest):
    url_view = 'url_shop_module_config_update'

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_existing_module_get(self):
        super().not_existing_module_get()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopModuleCategoryCreateViewTests(BaseGeneralShopModuleViewsTest):
    url_view = 'url_shop_module_category_create'

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_existing_module_get(self):
        super().not_existing_module_get()

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

    def get_url(self, shop_pk, module_class, category_pk):
        return reverse(self.url_view, kwargs={'shop_pk': shop_pk, 'module_class': module_class, 'category_pk': category_pk})

    def chief_get(self):
        response_client3_selfsales = self.client3.get(self.get_url(self.shop1.pk, 'self_sales', self.category1.pk))
        self.assertEqual(response_client3_selfsales.status_code, 200)
        response_client3_operatorsales = self.client3.get(self.get_url(self.shop1.pk, 'operator_sales', self.category2.pk))
        self.assertEqual(response_client3_operatorsales.status_code, 200)

    def not_allowed_user_get(self):
        response_client2_selfsales = self.client2.get(self.get_url(self.shop1.pk, 'self_sales', self.category1.pk))
        self.assertEqual(response_client2_selfsales.status_code, 403)
        response_client2_operatorsales = self.client2.get(self.get_url(self.shop1.pk, 'operator_sales', self.category2.pk))
        self.assertEqual(response_client2_operatorsales.status_code, 403)

    def not_existing_shop_get(self):
        response_client3 = self.client3.get(self.get_url('5353', 'self_sales', self.category1.pk))
        self.assertEqual(response_client3.status_code, 404)

    def not_existing_module_get(self):
        response_client3 = self.client3.get(self.get_url(self.shop1.pk, 'NE_module', self.category1.pk))
        self.assertEqual(response_client3.status_code, 404)

    def not_existing_category_get(self):
        response_client3 = self.client3.get(self.get_url(self.shop1.pk, 'self_sales', 5353))
        self.assertEqual(response_client3.status_code, 404)

    def category_not_in_shop(self):
        response_client3 = self.client3.get(self.get_url(self.shop2.pk, 'self_sales', self.category1.pk))
        self.assertEqual(response_client3.status_code, 404)

    def category_not_in_module(self):
        response_client3 = self.client3.get(self.get_url(self.shop1.pk, 'self_sales', self.category2.pk))
        self.assertEqual(response_client3.status_code, 404)

    def offline_user_redirection(self):
        """
        Test offline user redirection to login page
        """
        response_offline_user_selfsales = Client().get(
            self.get_url(self.shop1.pk, 'self_sales', self.category1.pk))
        response_offline_user_operatorsales = Client().get(
            self.get_url(self.shop1.pk, 'operator_sales', self.category2.pk))
        self.assertEqual(response_offline_user_selfsales.status_code, 302)
        self.assertRedirects(response_offline_user_selfsales, get_login_url_redirected(self.get_url(self.shop1.pk, 'self_sales', self.category1.pk)))
        self.assertEqual(response_offline_user_operatorsales.status_code, 302)
        self.assertRedirects(
            response_offline_user_operatorsales, get_login_url_redirected(self.get_url(self.shop1.pk, 'operator_sales', self.category2.pk)))


class ShopModuleCategoryUpdateViewTests(BaseFocusShopModuleCategoryViewsTest):
    url_view = 'url_shop_module_category_update'

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_existing_module_get(self):
        super().not_existing_module_get()

    def test_not_existing_category_get(self):
        super().not_existing_category_get()

    def test_category_not_in_shop(self):
        super().category_not_in_shop()

    def test_category_not_in_module(self):
        super().category_not_in_module()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()


class ShopModuleCategoryDeleteViewTests(BaseFocusShopModuleCategoryViewsTest):
    url_view = 'url_shop_module_category_delete'

    def test_chief_get(self):
        super().chief_get()

    def test_not_allowed_user_get(self):
        super().not_allowed_user_get()

    def test_not_existing_shop_get(self):
        super().not_existing_shop_get()

    def test_not_existing_module_get(self):
        super().not_existing_module_get()

    def test_not_existing_category_get(self):
        super().not_existing_category_get()

    def test_category_not_in_shop(self):
        super().category_not_in_shop()

    def test_category_not_in_module(self):
        super().category_not_in_module()

    def test_offline_user_redirection(self):
        super().offline_user_redirection()
