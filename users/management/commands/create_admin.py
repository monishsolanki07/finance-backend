import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates the initial admin user from environment variables if not already exists.'

    def handle(self, *args, **kwargs):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        # ✅ Validate all env vars are present
        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR(
                'Missing environment variables. '
                'Please set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD.'
            ))
            return

        # ✅ Skip if admin already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Admin user "{username}" already exists. Skipping creation.'
            ))
            return

        # ✅ create_superuser also sets role='admin' via our custom UserManager
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(self.style.SUCCESS(
            f'Admin user "{username}" created successfully with role=admin.'
        ))