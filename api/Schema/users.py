import graphene
from graphene_django.types import DjangoObjectType

from users.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('pk', 'username', 'last_name', 'first_name', 'email',
                       'surname', 'family', 'campus', 'year', 'avatar',
                       'balance')


class UsersQuery(graphene.AbstractType):
    user = graphene.Field(UserType, id=graphene.ID())

    def resolve_user(self, args, context, info):
        return User.objects.get(pk=args.get('id'))
