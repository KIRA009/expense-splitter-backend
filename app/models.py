from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
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
        return f"{self.from_user.contact} to {self.to_user.contact}"


class Friend(models.Model):
    current_user = models.ForeignKey(User,
                                     on_delete=models.CASCADE,
                                     related_name="user")
    friend = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="friend")
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.current_user.contact} is friends with {self.friend.contact}"

    @staticmethod
    def accept(current_user, friend):
        relation = Friend.objects.create(
            current_user=current_user,
            friend=friend
        )
        rev_relation = Friend.objects.create(
            current_user=friend,
            friend=current_user
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


class Group(models.Model):
    group_name = models.CharField(max_length=15)
    group_admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_admin")
    group_member = models.ManyToManyField(User, related_name="group_member")

    def __str__(self):
        return f"{self.group_admin.contact}'s {self.group_name}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_of_initation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.contact} at {self.time_of_initation}"


class PaymentHolder(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="payment_holders")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_user")
    amount_owed = models.IntegerField()
    paid = models.BooleanField(default=False)
    payment_datetime = models.DateTimeField(default=None)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.contact} owes {self.amount_owed}"