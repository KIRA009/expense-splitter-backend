import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from django.contrib.auth import authenticate

from .models import User
from .decorators import login_required


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query(ObjectType):
    user = graphene.Field(UserType, contact=graphene.String())
    login_user = graphene.Field(UserType, contact=graphene.String(), password=graphene.String())

    @login_required
    def resolve_user(self, info, **kwargs):
        contact = kwargs.get('contact')
        try:
            user = User.objects.get_by_natural_key(username=contact)
            return user
        except User.DoesNotExist:
            return None

    def resolve_login_user(self, info, **kwargs):
        contact = kwargs.get('contact')
        password = kwargs.get('password')
        user = authenticate(username=contact, password=password)
        if user:
            info.context.user = user
            return user
        return None


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


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
