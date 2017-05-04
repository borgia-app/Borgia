import graphene

from api.Schema.shops import ShopsQuery
from api.Schema.modules import ModulesQuery


class Query(ShopsQuery,
            ModulesQuery,
            graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
