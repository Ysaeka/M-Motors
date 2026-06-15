# Models here

from django.db import models


class Vehicle(models.Model):
    class FuelType(models.TextChoices):
        GASOLINE = "gasoline", "Essence"
        DIESEL = "diesel", "Diesel"
        HYBRID = "hybrid", "Hybride"
        ELECTRIC = "electric", "Électrique"

    class GearboxType(models.TextChoices):
        MANUAL = "manual", "Manuelle"
        AUTOMATIC = "automatic", "Automatique"

    class OfferType(models.TextChoices):
        SALE = "sale", "Achat"
        LLD = "lld", "Location"
        BOTH = "both", "Achat et location"

    class AvailabilityStatus(models.TextChoices):
        AVAILABLE = "available", "Disponible"
        RESERVED = "reserved", "Réservé"
        UNAVAILABLE = "unavailable", "Indisponible"
        SOLD = "sold", "Vendu"
        RENTED = "rented", "Loué"

    reference = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    trim = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    image = models.ImageField(
        upload_to="vehicles/",
        max_length=255,
        blank=True,
    )
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices)
    gearbox = models.CharField(max_length=20, choices=GearboxType.choices)
    price_sale = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    offer_type = models.CharField(max_length=20, choices=OfferType.choices)
    availability_status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.reference})"
    
    @property
    def offer_label(self):
        if self.offer_type == self.OfferType.SALE:
            return "Achat"
        if self.offer_type == self.OfferType.LLD:
            return "Location"
        if self.offer_type == self.OfferType.BOTH:
            return "Achat & Location"
        return ""

    @property
    def has_lld_options(self):
        return self.offer_type in [self.OfferType.LLD, self.OfferType.BOTH]
