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
        UNDER_REVIEW = "under_review", "En cours d'examen"
        APPROVED = "approved", "Accepté"
        REJECTED = "rejected", "Refusé"

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
    options = models.ManyToManyField(Option, blank=True, related_name="dossiers")
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dossier #{self.id} - {self.customer}"


class Document(models.Model):
    class DocumentType(models.TextChoices):
        ID_CARD = "id_card", "Carte d'identité"
        DRIVER_LICENSE = "driver_license", "Permis de conduire"
        PROOF_OF_ADDRESS = "proof_of_address", "Justificatif de domicile"
        PROOF_OF_INCOME = "proof_of_income", "Justificatif de revenus"
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
