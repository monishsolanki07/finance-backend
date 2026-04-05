from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

ROLES = [
    ('viewer', 'Viewer'),
    ('analyst', 'Analyst'),
    ('admin', 'Admin'),
]


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # ✅ always hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        # ✅ superuser also gets admin role in our system
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    # AbstractUser already has: username, email, password, is_active, is_staff, is_superuser
    role = models.CharField(max_length=10, choices=ROLES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.role})"