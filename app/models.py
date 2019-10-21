from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser):
    contact = models.CharField(max_length=10, unique=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'contact'

    objects = UserManager()

    def __str__(self):
        return self.contact
