from django.conf import settings
from django.db import models


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    address = models.TextField("Adresse", blank=True)

    def __str__(self):
        return f"Profil client - {self.user.get_full_name() or self.user.username}"
    