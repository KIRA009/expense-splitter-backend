from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, details, verified=False):
        """
        Creates and saves a User with the given contact, password
        """
        password = details['password']
        del details['password']
        # del details['csrfmiddlewaretoken']
        user = self.model(**details)
        user.set_password(password)
        user.save(using=self._db)
        return user
