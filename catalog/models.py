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

    # Caractéristiques détaillées du véhicule.
    # Ces champs sont optionnels pour ne pas casser les véhicules déjà existants.
    color = models.CharField("Couleur", max_length=50, blank=True)
    doors = models.PositiveSmallIntegerField("Nombre de portes", null=True, blank=True)
    seats = models.PositiveSmallIntegerField("Nombre de places", null=True, blank=True)
    fiscal_power = models.PositiveSmallIntegerField("Puissance fiscale", null=True, blank=True)
    power_hp = models.PositiveIntegerField("Puissance DIN", null=True, blank=True)
    co2_emissions = models.PositiveIntegerField("Émissions CO2", null=True, blank=True)
    consumption = models.DecimalField(
        "Consommation moyenne",
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )
    crit_air = models.CharField("Crit’Air", max_length=20, blank=True)
    warranty = models.CharField("Garantie", max_length=100, blank=True)

    # Liste simple des équipements inclus.
    # Exemple : GPS, Bluetooth, Caméra de recul, Climatisation automatique
    included_options = models.TextField("Options incluses", blank=True)

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

    @property
    def included_options_list(self):
        """
        Transforme le texte des options incluses en liste exploitable dans le template.

        Exemple :
        "GPS, Bluetooth, Caméra de recul"
        devient :
        ["GPS", "Bluetooth", "Caméra de recul"]
        """
        options = self.included_options.replace("\n", ",").split(",")
        return [option.strip() for option in options if option.strip()]