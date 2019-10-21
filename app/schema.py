import graphene
from graphene_django.types import DjangoObjectType, ObjectType

from .models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query(ObjectType):
    user = graphene.Field(UserType, contact=graphene.String())
    users = graphene.List(UserType)

    def resolve_user(self, info, **kwargs):
        contact = kwargs.get('contact')
        try:
            user = User.objects.get_by_natural_key(username=contact)
            return user
        except User.DoesNotExist:
            return None

    def resolve_users(self, info, **kwargs):
        return User.objects.all()


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
