import graphene

from api.Schema.shops import ShopsQuery
from api.Schema.modules import ModulesQuery
from api.Schema.users import UsersQuery


class Query(ShopsQuery,
            ModulesQuery,
            UsersQuery,
            graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
