from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)  # Normalize email to avoid duplicates
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.is_staff = True  # Required for admin access
        user.is_superuser = True  # Required for superuser privileges
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email):
        return self.get(**{self.model.USERNAME_FIELD: email})

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

class MyUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=111)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=16)
    avatar = models.ImageField(upload_to='media/user/avatars', blank=True, null=True)  # Optional field
    address = models.CharField(max_length=100, blank=True)  # Optional field
    created_date = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # Required for admin access

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username






