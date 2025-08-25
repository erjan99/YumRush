from django.contrib.auth.base_user import BaseUserManager


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
        user.is_superuser = True  # Required for superuser privileges
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email):
        return self.get(**{self.model.USERNAME_FIELD: email})


from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class MyUser(AbstractBaseUser):
    email = models.EmailField(max_length=255)
    username = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to='media/user_avatars/', blank=True, null=True)
    address = models.TextField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)

    objects = MyUserManager()

    ROLE_CHOICES = (
        ('user', 'User'),
        ('manager', 'Manager'),
        ('courier', 'Courier'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
