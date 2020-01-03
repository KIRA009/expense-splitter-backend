import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from django.contrib.auth import authenticate
from django.db.models import Q

from .models import User, FriendRequest, Friend, Group, Member
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


class GroupType(DjangoObjectType):
    class Meta:
        model = Group


class MemberType(DjangoObjectType):
    class Meta:
        model = Member        


class Query(ObjectType):
    user = graphene.Field(UserType, contact=graphene.String())
    friend_requests_sent = graphene.List(FriendRequestType)
    friend_requests_received = graphene.List(FriendRequestType)
    friends = graphene.List(FriendType)
    groups = graphene.List(GroupType)

    @login_required
    def resolve_user(self, info, **kwargs):
        return info.context.user

    @login_required
    def resolve_friend_requests_sent(self, info, **kwargs):
        return FriendRequest.objects.filter(from_user=info.context.user)
    
    @login_required
    def resolve_friend_requests_received(self, info, **kwargs):
        return FriendRequest.objects.filter(to_user=info.context.user)

    @login_required
    def resolve_friends(self, info, **kwargs):
        return Friend.objects.filter(current_user=info.context.user)

    @login_required
    def resolve_groups(self, info, **kwargs):
        if Member.objects.filter(user=info.context.user).exists():
            return Group.objects.filter(group_admin=info.context.user) | Group.objects.filter(group_member=Member.objects.get(user=info.context.user))
        else:
            return Group.objects.filter(group_admin=info.context.user)

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
    message = graphene.String()
    user_receiver = graphene.Field(UserType)
    friend_request = graphene.Field(FriendRequestType)

    @staticmethod
    @login_required
    def mutate(root, info, contact_receiver):
        try:
            user_receiver = User.objects.get_by_natural_key(contact_receiver)
            if user_receiver == info.context.user:
                return SendFriendRequest(message="Users can't send request to themselves", ok=False, user_receiver=user_receiver, friend_request=None)

        except User.DoesNotExist:
            return SendFriendRequest(message="user not found", ok=False, user_receiver=None, friend_request=None)

        try:
            friend_request = FriendRequest.objects.get(from_user=info.context.user, to_user=user_receiver)
            return SendFriendRequest(message="A friend request has already been sent", ok=False, user_receiver=user_receiver, friend_request=None)

        except FriendRequest.DoesNotExist:
            if FriendRequest.objects.filter(from_user=user_receiver, to_user=info.context.user).exists():
                return SendFriendRequest(message="User has sent a request before", ok=False, user_receiver=user_receiver, friend_request=None)

            if Friend.objects.filter(current_user=info.context.user, friend=user_receiver).exists():
                return SendFriendRequest(message="Both users are already friends", ok=False, user_receiver=user_receiver, friend_request=None)
            
            friend_request = FriendRequest.objects.create(from_user=info.context.user, to_user=user_receiver)
            return SendFriendRequest(message="Friend request sent successfully", ok=True, user_receiver=user_receiver, friend_request=friend_request)


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
        other_user = graphene.String()
    ok = graphene.Boolean()
    other_user = graphene.Field(UserType)
    friend_request = graphene.Field(FriendRequestType)

    @staticmethod
    @login_required
    def mutate(root, info, other_user):
        try:
            other_user = User.objects.get_by_natural_key(other_user)
        except User.DoesNotExist:
            return DeleteFriendRequest(ok=False, other_user=None, friend_request=None)

        try:
            friend_request = FriendRequest.objects.get(Q(from_user=info.context.user, to_user=other_user) | Q(
                from_user=other_user, to_user=info.context.user))
            friend_request.delete()
            return DeleteFriendRequest(ok=True, other_user=other_user, friend_request=friend_request)
        except FriendRequest.DoesNotExist:
            return DeleteFriendRequest(ok=False, other_user=other_user, friend_request=None)


class CreateGroup(graphene.Mutation):
    class Arguments:
        group_name = graphene.String()
        contacts_list = graphene.List(graphene.String)
    message = graphene.String()
    ok = graphene.Boolean()
    group = graphene.Field(GroupType)

    @staticmethod
    @login_required
    def mutate(root, info, group_name, contacts_list):
        try:
            group = Group.objects.get(group_name=group_name, group_admin=info.context.user)
            return CreateGroup(ok=False, message="A group with the same name already exists", group=None)
        except Group.DoesNotExist:
            # to remove duplicate contacts
            contacts_list = list(set(contacts_list))
            friends_contacts_list = [ str(fri_obj.friend.contact) for fri_obj in Friend.objects.filter(current_user=info.context.user) ]
            for contact in contacts_list:
                if contact not in friends_contacts_list:
                    return CreateGroup(ok=False, message="Some contacts are not of your friends'", group=None)
            # create group with the members(selected friends)
            group = Group.objects.create(group_name=group_name, group_admin=info.context.user)
            for contact in contacts_list:
                member, created = Member.objects.get_or_create(user=User.objects.get(contact=contact))
                group.group_member.add(member.id)
            return CreateGroup(ok=True, message="Group created successfully", group=group)


class AddMembers(graphene.Mutation):
    class Arguments:
        group_name = graphene.String()
        contacts_list = graphene.List(graphene.String)
    message = graphene.String()
    ok = graphene.Boolean()
    group = graphene.Field(GroupType)

    @staticmethod
    @login_required
    def mutate(root, info, group_name, contacts_list):
        try:
            # to remove duplicate contacts
            contacts_list = list(set(contacts_list))
            friends_contacts_list = [ str(fri_obj.friend.contact) for fri_obj in Friend.objects.filter(current_user=info.context.user) ]
            for contact in contacts_list:
                if contact not in friends_contacts_list:
                    return AddMembers(ok=False, message="Some contacts are not of your friends'", group=None)
            group = Group.objects.get(group_name=group_name, group_admin=info.context.user)
            members_list = [ member_obj.user.contact for member_obj in group.group_member.all() ]
            for contact in contacts_list:
                if contact not in members_list:
                    member, created = Member.objects.get_or_create(user=User.objects.get(contact=contact))
                    group.group_member.add(member.id)
            return AddMembers(ok=True, message="Successfully added new members", group=group)
        except Group.DoesNotExist:
            return AddMembers(ok=False, message="Group doesn't exist", group=None)


class RemoveMembers(graphene.Mutation):
    class Arguments:
        group_name = graphene.String()
        contacts_list = graphene.List(graphene.String)
    message = graphene.String()
    ok = graphene.Boolean()
    group = graphene.Field(GroupType)

    @staticmethod
    @login_required
    def mutate(root, info, group_name, contacts_list):
        try:
            # to remove duplicate contacts
            contacts_list = list(set(contacts_list))
            group = Group.objects.get(group_name=group_name, group_admin=info.context.user)
            members_list = [ member_obj.user.contact for member_obj in group.group_member.all() ]
            for contact in contacts_list:
                if contact in members_list:
                    group.group_member.remove(Member.objects.get(user=User.objects.get(contact=contact)))
            return RemoveMembers(ok=True, message="Successfully removed", group=group)
        except Group.DoesNotExist:
            return RemoveMembers(ok=False, message="Group doesn't exist", group=None)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
    send_friend_request = SendFriendRequest.Field()
    accept_friend_request = AcceptFriendRequest.Field()
    delete_friend_request = DeleteFriendRequest.Field()
    create_group = CreateGroup.Field()
    add_members = AddMembers.Field()
    remove_members = RemoveMembers.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
