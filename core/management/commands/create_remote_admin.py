import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée un superuser distant si absent"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(
                self.style.ERROR(
                    "Variables DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL ou DJANGO_SUPERUSER_PASSWORD manquantes."
                )
            )
            return

        user = User.objects.filter(username=username).first()

        if user:
            self.stdout.write(self.style.WARNING(f"Le superuser '{username}' existe déjà."))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' créé avec succès."))