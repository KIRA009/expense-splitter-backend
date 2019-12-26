import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from django.contrib.auth import authenticate

from .models import User, FriendRequest, Friend
from .decorators import login_required
from .utils import make_hash


class UserType(DjangoObjectType):
    class Meta:
        model = User


class FriendRequestType(DjangoObjectType):
    class Meta:
        model = FriendRequest


class FriendType(DjangoObjectType):
    class Meta:
        model = Friend


class Query(ObjectType):
    user = graphene.Field(UserType, contact=graphene.String())
    friend_request = graphene.Field(FriendRequestType, contact_receiver=graphene.String())

    @login_required
    def resolve_user(parent, info, **kwargs):
        contact = kwargs.get('contact')
        try:
            user = User.objects.get_by_natural_key(username=contact)
            return user
        except User.DoesNotExist:
            return None

    @login_required
    def resolve_friend_request(parent, info, **kwargs):
        contact_receiver = kwargs.get('contact_receiver')
        try:
            friend_request = FriendRequest.objects.get(from_user=info.context.user, to_user__username=contact_receiver)
            return friend_request
        except FriendRequest.DoesNotExist:
            return None

    @login_required
    def resolve_friend(parent, info, **kwargs):
        contact_sender = kwargs.get('contact_sender')
        try:
            friend = Friend.objects.get(current_user=info.context.user, friend__username=contact_sender)
            return friend
        except Friend.DoesNotExist:
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


class SendFriendRequest(graphene.Mutation):
    class Arguments:
        contact_receiver = graphene.String()
    ok = graphene.Boolean()
    user_receiver = graphene.Field(UserType)
    friend_request = graphene.Field(FriendRequestType)

    @staticmethod
    @login_required
    def mutate(root, info, contact_receiver):
        try:
            user_receiver = User.objects.get_by_natural_key(contact_receiver)

        except User.DoesNotExist:
            return SendFriendRequest(ok=False, user_receiver=None, friend_request=None)

        try:
            friend_request = FriendRequest.objects.get(from_user=info.context.user, to_user=user_receiver)
            return SendFriendRequest(ok=False, user_receiver=user_receiver, friend_request=None)

        except FriendRequest.DoesNotExist:
            friend_request = FriendRequest.objects.create(from_user=info.context.user, to_user=user_receiver)
            return SendFriendRequest(ok=True, user_receiver=user_receiver, friend_request=friend_request)


class AcceptFriendRequest(graphene.Mutation):
    class Arguments:
        contact_sender = graphene.String()
    ok = graphene.Boolean()
    user_sender = graphene.Field(UserType)
    friend_request = graphene.Field(FriendRequestType)
    friend = graphene.Field(FriendType)

    @staticmethod
    @login_required
    def mutate(root, info, contact_sender):
        try:
            user_sender = User.objects.get_by_natural_key(contact_sender)

        except User.DoesNotExist:
            return AcceptFriendRequest(ok=False, user_sender=None, friend_request=None, friend=None)

        try:
            friend_request = FriendRequest.objects.get(from_user=user_sender, to_user=info.context.user)
            friend = Friend.accept(current_user=info.context.user, friend=user_sender)
            return AcceptFriendRequest(ok=True, user_sender=user_sender, friend_request=friend_request, friend=friend)

        except FriendRequest.DoesNotExist:
            return AcceptFriendRequest(ok=False, user_sender=user_sender, friend_request=None, friend=None)


class DeleteFriendRequest(graphene.Mutation):
    class Arguments:
        contact_sender = graphene.String()
    ok = graphene.Boolean()
    user_sender = graphene.Field(UserType)
    friend_request = graphene.Field(FriendRequestType)

    @staticmethod
    @login_required
    def mutate(root, info, contact_sender):
        try:
            user_sender = User.objects.get_by_natural_key(contact_sender)

        except User.DoesNotExist:
            return DeleteFriendRequest(ok=False, user_sender=None, friend_request=None)

        try:
            friend_request = FriendRequest.objects.get(from_user=user_sender, to_user=info.context.user)
            friend_request.delete()
            return DeleteFriendRequest(ok=True, user_sender=user_sender, friend_request=friend_request)

        except FriendRequest.DoesNotExist:
            return DeleteFriendRequest(ok=False, user_sender=user_sender, friend_request=None)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
    send_friend_request = SendFriendRequest.Field()
    accept_friend_request = AcceptFriendRequest.Field()
    delete_friend_request = DeleteFriendRequest.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
