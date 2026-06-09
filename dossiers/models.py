# Models for files

from django.conf import settings
from django.db import models

from catalog.models import Vehicle


class Option(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default_in_lld = models.BooleanField(default=False)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Dossier(models.Model):
    class ApplicationType(models.TextChoices):
        SALE = "sale", "Achat"
        LLD = "lld", "Location"

    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        SUBMITTED = "submitted", "Soumis"
        UNDER_REVIEW = "under_review", "En cours d'instruction"
        APPROVED = "approved", "Accepté"
        REJECTED = "rejected", "Refusé"

    class HousingStatus(models.TextChoices):
        TENANT = "tenant", "Locataire"
        OWNER = "owner", "Propriétaire"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dossiers",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="dossiers",
    )
    application_type = models.CharField(max_length=20, choices=ApplicationType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    customer_note = models.TextField(blank=True)
    internal_note = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    housing_status = models.CharField(max_length=20,choices=HousingStatus.choices,blank=True,)
    monthly_rent = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    has_current_credit = models.BooleanField(default=False)
    monthly_credit_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,)
    data_processing_consent = models.BooleanField(default=False)
    data_processing_consent_at = models.DateTimeField(null=True, blank=True)
    options = models.ManyToManyField(Option, blank=True, related_name="dossiers")
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dossier #{self.id} - {self.customer}"
    class LLDDuration(models.IntegerChoices):
        MONTHS_24 = 24, "24 mois"
        MONTHS_36 = 36, "36 mois"
        MONTHS_48 = 48, "48 mois"
        MONTHS_60 = 60, "60 mois"
        MONTHS_72 = 72, "72 mois"
        MONTHS_84 = 84, "84 mois"

    lld_duration_months = models.PositiveSmallIntegerField(
        choices=LLDDuration.choices,
        null=True,
        blank=True,
    )

class Document(models.Model):
    class DocumentType(models.TextChoices):
        ID_CARD = "id_card", "Carte d'identité"
        DRIVER_LICENSE = "driver_license", "Permis de conduire"
        PROOF_OF_ADDRESS = "proof_of_address", "Justificatif de domicile"
        PROOF_OF_INCOME = "proof_of_income", "Justificatif de revenus"
        TAX_NOTICE = "tax_notice", "Avis d'imposition"
        RENT_RECEIPT = "rent_receipt", "Quittance de loyer"
        OTHER = "other", "Autre"

    class ValidationStatus(models.TextChoices):
        PENDING = "pending", "En attente"
        APPROVED = "approved", "Validé"
        REJECTED = "rejected", "Refusé"

    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    file = models.FileField(upload_to="documents/")
    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
    )
    comment = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.document_type} - Dossier #{self.dossier.id}"


class DossierStatusHistory(models.Model):
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="status_changes",
    )
    old_status = models.CharField(max_length=20, choices=Dossier.Status.choices)
    new_status = models.CharField(max_length=20, choices=Dossier.Status.choices)
    comment = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.old_status} -> {self.new_status} (Dossier #{self.dossier.id})"
