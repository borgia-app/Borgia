import graphene
from graphene_django.types import DjangoObjectType, ObjectType

from shops.models import (Shop, ContainerCase)


class ShopType(DjangoObjectType):
    class Meta:
        model = Shop


class ProductBaseType(ObjectType):
    pk = graphene.ID()
    name = graphene.String()
    is_single_product = graphene.Boolean()
    usual_price = graphene.Float()
    usual_quantity = graphene.Float()

    def resolve_pk(self, args, context, info):
        return self.pk

    def resolve_name(self, args, context, info):
        return self.__str__()

    def resolve_is_single_product(self, args, context, info):
        if self.product_unit:
            return False
        return True

    def resolve_usual_price(self, args, context, info):
        return self.get_moded_usual_price()

    def resolve_usual_quantity(self, args, context, info):
        if self.product_unit:
            return self.product_unit.usual_quantity()
        return None


class ContainerType(ObjectType):
    pk = graphene.ID()
    name = graphene.String()
    usual_price = graphene.Float()
    usual_quantity = graphene.Float()

    def resolve_pk(self, args, context, info):
        return self.pk

    def resolve_name(self, args, context, info):
        return self.product_base.__str__()

    def resolve_usual_price(self, args, context, info):
        return self.product_base.get_moded_usual_price()

    def resolve_usual_quantity(self, args, context, info):
        return self.product_base.product_unit.usual_quantity()


class ContainerCaseType(ObjectType):
    pk = graphene.ID()
    name = graphene.String()
    container = graphene.Field(ContainerType)

    def resolve_pk(self, args, context, info):
        return self.pk

    def resolve_name(self, args, context, info):
        return self.__str__()

    def resolve_container(self, args, context, info):
        return self.product


class ShopsQuery(graphene.AbstractType):
    pass
