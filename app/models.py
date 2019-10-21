from django.contrib.auth.models import AbstractBaseUser
from django.db import models

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
