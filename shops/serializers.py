from rest_framework import serializers
from shops.models import ProductBase, ProductUnit, Shop


class ProductBaseSerializer(serializers.HyperlinkedModelSerializer):
    product_unit = serializers.HyperlinkedRelatedField(view_name='url_api_retrieveudatedestroy_productunit', read_only=True)
    shop = serializers.HyperlinkedRelatedField(view_name='url_api_retrieveudatedestroy_shop', read_only=True)

    class Meta:
        model = ProductBase
        fields = ('name', 'description', 'is_manual', 'brand', 'type', 'shop', 'quantity', 'product_unit', 'is_active')


class ProductUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductUnit
        fields = ('name', 'description', 'unit', 'type', 'is_active')


class ShopSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('name', 'description')