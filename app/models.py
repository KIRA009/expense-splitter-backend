from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser):
    contact = models.CharField(max_length=10, unique=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=256, default='First Name')
    last_name = models.CharField(max_length=256, default='Last Name')
    USERNAME_FIELD = 'contact'

    objects = UserManager()

    def __str__(self):
        return self.contact


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_sent",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_received",
    )

    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.from_user.username} to {self.to_user.username}"


class Friend(models.Model):
    current_user = models.ForeignKey(User, 
        on_delete=models.CASCADE, 
        related_name="user")
    friend = models.ForeignKey(User, 
        on_delete=models.CASCADE, 
        related_name="friend")
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.current_user.username} is friends with {self.friend.username}"

    @staticmethod
    def accept(current_user, friend):
        relation = Friend.objects.create(
            current_user = current_user,
            friend = friend
            )
        rev_relation = Friend.objects.create(
            current_user = friend,
            friend = current_user
            )

        FriendRequest.objects.filter(
            from_user=friend,
            to_user=current_user).delete()

        return relation

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.current_user == self.friend:
            raise ValidationError("Users cannot be friends with themselves.")

        super(Friend, self).save(*args, **kwargs)