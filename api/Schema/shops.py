import graphene
from graphene_django.types import DjangoObjectType, ObjectType

from shops.models import (Shop, ContainerCase, ProductBase, ProductUnit,
                          Container, SingleProduct)


class ShopType(DjangoObjectType):
    class Meta:
        model = Shop


class ContainerCase(DjangoObjectType):
    class Meta:
        model = ContainerCase

class ProductBase(DjangoObjectType):
    class Meta:
        model = ProductBase

class ProductUnit(DjangoObjectType):
    class Meta:
        model = ProductUnit

class Container(DjangoObjectType):
    class Meta:
        model = Container

class SingleProduct(DjangoObjectType):
    class Meta:
        model = SingleProduct

class Query(graphene.AbstractType):
    all_shops = graphene.List(ShopType)
    shop = graphene.Field(ShopType, id=graphene.ID(),
                          description='The shop according to the ID')

    def resolve_all_shops(self, args, context, info):
        return Shop.objects.all()

    def resolve_shop(self, args, context, info):
        return Shop.objects.get(pk=args.get('id'))
