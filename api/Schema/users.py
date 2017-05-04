import graphene
from graphene_django.types import DjangoObjectType

from users.models import User

from django.contrib.auth import authenticate


class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('pk', 'username', 'last_name', 'first_name', 'email',
                       'surname', 'family', 'campus', 'year', 'avatar',
                       'balance')


class LoginUser(graphene.Mutation):
    class Input:
        username = graphene.String()
        password = graphene.String()

    user = graphene.Field(lambda: graphene.Boolean)

    def mutate(root, args, context, info):
        u = authenticate(username=args.get('username'),
                         password=args.get('password'))
        if u is not None:
            return LoginUser(user=True)
        return LoginUser(user=False)


class UsersQuery(graphene.AbstractType):
    user = graphene.Field(UserType, id=graphene.ID())

    def resolve_user(self, args, context, info):
        return User.objects.get(pk=args.get('id'))


class UsersMutation(graphene.AbstractType):
    login_user = LoginUser.Field()
