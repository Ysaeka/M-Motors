from django.contrib import admin
from django.utils import timezone

from .models import Dossier, Document, DossierStatusHistory, Option, DossierAdvisorMessage


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "is_default_in_lld", "monthly_price")
    list_filter = ("is_active", "is_default_in_lld")
    search_fields = ("code", "name")


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "vehicle",
        "application_type",
        "status",
        "created_at",
        "submitted_at",
        "reviewed_at",
    )
    list_filter = ("application_type", "status", "created_at", "reviewed_at")
    search_fields = (
        "customer__username",
        "customer__email",
        "vehicle__reference",
        "vehicle__brand",
        "vehicle__model",
    )
    readonly_fields = ("created_at", "updated_at", "submitted_at", "reviewed_at")
    actions = ("mark_under_review", "approve_dossiers", "reject_dossiers")

    @admin.action(description="Passer en cours d'instruction")
    def mark_under_review(self, request, queryset):
        for dossier in queryset:
            old_status = dossier.status
            dossier.status = Dossier.Status.UNDER_REVIEW
            dossier.reviewed_at = timezone.now()
            dossier.save(update_fields=["status", "reviewed_at", "updated_at"])

            DossierStatusHistory.objects.create(
                dossier=dossier,
                old_status=old_status,
                new_status=Dossier.Status.UNDER_REVIEW,
                changed_by=request.user,
                comment="Statut mis à jour depuis le back-office.",
            )

    @admin.action(description="Accepter les dossiers sélectionnés")
    def approve_dossiers(self, request, queryset):
        for dossier in queryset:
            old_status = dossier.status
            dossier.status = Dossier.Status.APPROVED
            dossier.reviewed_at = timezone.now()
            dossier.save(update_fields=["status", "reviewed_at", "updated_at"])

            DossierStatusHistory.objects.create(
                dossier=dossier,
                old_status=old_status,
                new_status=Dossier.Status.APPROVED,
                changed_by=request.user,
                comment="Dossier accepté depuis le back-office.",
            )

    @admin.action(description="Refuser les dossiers sélectionnés")
    def reject_dossiers(self, request, queryset):
        for dossier in queryset:
            old_status = dossier.status
            dossier.status = Dossier.Status.REJECTED
            dossier.reviewed_at = timezone.now()
            dossier.save(update_fields=["status", "reviewed_at", "updated_at"])

            DossierStatusHistory.objects.create(
                dossier=dossier,
                old_status=old_status,
                new_status=Dossier.Status.REJECTED,
                changed_by=request.user,
                comment="Dossier refusé depuis le back-office.",
            )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dossier",
        "document_type",
        "validation_status",
        "uploaded_at",
        "validated_at",
    )
    list_filter = ("document_type", "validation_status")
    search_fields = ("dossier__id",)
    actions = ("validate_documents", "reject_documents")

    @admin.action(description="Valider les documents sélectionnés")
    def validate_documents(self, request, queryset):
        queryset.update(
            validation_status=Document.ValidationStatus.VALIDATED,
            validated_at=timezone.now(),
        )

    @admin.action(description="Refuser les documents sélectionnés")
    def reject_documents(self, request, queryset):
        queryset.update(
            validation_status=Document.ValidationStatus.REJECTED,
            validated_at=timezone.now(),
        )


@admin.register(DossierStatusHistory)
class DossierStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dossier",
        "old_status",
        "new_status",
        "changed_by",
        "created_at",
    )
    list_filter = ("old_status", "new_status", "created_at")
    search_fields = ("dossier__id", "changed_by__username")


@admin.register(DossierAdvisorMessage)
class DossierAdvisorMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dossier",
        "customer",
        "subject",
        "is_read",
        "created_at",
    )
    list_filter = ("is_read", "created_at")
    search_fields = (
        "dossier__id",
        "customer__username",
        "customer__email",
        "subject",
        "message",
    )
    readonly_fields = (
        "dossier",
        "customer",
        "subject",
        "message",
        "created_at",
    )