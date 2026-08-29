from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager — email is the unique identifier instead of username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Extended user model for KalpAahar."""

    email          = models.EmailField(unique=True)
    name           = models.CharField(max_length=200, blank=True)
    phone          = models.CharField(max_length=20, blank=True)
    email_verified = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    # Use email as the login field
    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []          # removes 'email' from createsuperuser prompts

    objects = UserManager()

    class Meta:
        verbose_name       = "User"
        verbose_name_plural = "Users"
        ordering           = ["-created_at"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name or self.email
