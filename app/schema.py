import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from django.contrib.auth import authenticate

from .models import User
from .decorators import login_required
from .utils import make_hash


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query(ObjectType):
    user = graphene.Field(UserType, contact=graphene.String())

    @login_required
    def resolve_user(self, info, **kwargs):
        return info.context.user


class CreateUser(graphene.Mutation):
    class Arguments:
        contact = graphene.String()
        password = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
    ok = graphene.Boolean()
    user = graphene.Field(UserType)

    @staticmethod
    def mutate(root, info, contact, password, first_name, last_name):
        try:
            user = User.objects.get_by_natural_key(contact)
            return CreateUser(ok=False, user=None)
        except User.DoesNotExist:
            user = User.objects.create_user(dict(contact=contact, password=password, first_name=first_name,
                                                 last_name=last_name))
            return CreateUser(ok=True, user=user)


class LoginUser(graphene.Mutation):
    class Arguments:
        contact = graphene.String()
        password = graphene.String()
    logged_in = graphene.Boolean()
    token = graphene.String()

    @staticmethod
    def mutate(root, info, contact, password):
        user = authenticate(username=contact, password=password)
        if not user:
            return LoginUser(logged_in=False, token=None)
        return LoginUser(logged_in=True, token=make_hash(user))


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
