import graphene
from graphene_django.types import ObjectType

from modules.models import SelfSaleModule
from api.Schema.shops import ProductBaseType, ShopType, ContainerCaseType


class CategoryType(ObjectType):
    pk = graphene.ID()
    name = graphene.String()
    product_bases = graphene.List(ProductBaseType)

    def resolve_pk(self, args, context, info):
        return self.pk

    def resolve_name(self, args, context, info):
        return self.name

    def resolve_product_bases(self, args, context, info):
        pbs = []
        for pb in self.product_bases.all():
            if pb.quantity_products_stock() > 0:
                pbs.append(pb)
        return pbs


class SelfSaleModuleType(ObjectType):
    pk = graphene.ID()
    categories = graphene.List(CategoryType)
    shop = graphene.Field(ShopType)
    container_cases = graphene.List(ContainerCaseType)

    def resolve_pk(self, args, context, info):
        return self.pk

    def resolve_categories(self, args, context, info):
        return self.categories.all()

    def resolve_shop(self, args, context, info):
        return self.shop

    def resolve_container_cases(self, args, context, info):
        return self.container_cases.all()


class ModulesQuery(graphene.AbstractType):
    all_selfsalemodule_enabled = graphene.List(SelfSaleModuleType)

    def resolve_all_selfsalemodule_enabled(self, args, context, info):
        return SelfSaleModule.objects.filter(state=True).exclude(shop__pk=1)
