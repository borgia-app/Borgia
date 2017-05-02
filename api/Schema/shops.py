import graphene
from graphene_django.types import DjangoObjectType

from shops.models import Shop


class ShopType(DjangoObjectType):
    class Meta:
        model = Shop

class Query(graphene.AbstractType):
    all_shops = graphene.List(ShopType)

    def resolve_all_shops(self, args, context, info):
        return Shop.objects.all()
