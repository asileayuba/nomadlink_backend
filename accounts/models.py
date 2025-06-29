from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, wallet_address=None, email=None, password=None, username=None, **extra_fields):
        if not wallet_address:
            raise ValueError("Wallet address is required")
        if not username:
            username = slugify(wallet_address) + '-' + uuid.uuid4().hex[:6]
        user = self.model(
            wallet_address=wallet_address,
            email=self.normalize_email(email) if email else None,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not email:
            raise ValueError('Superusers must have an email.')

        if 'wallet_address' not in extra_fields:
            extra_fields['wallet_address'] = f"admin-{uuid.uuid4().hex[:10]}"

        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    wallet_address = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'wallet_address'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
    def get_username(self):
        return self.username
