# Register your models here.

from django.contrib import admin

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
    )
    list_filter = ("application_type", "status", "created_at")
    search_fields = ("customer__username", "vehicle__reference", "vehicle__brand", "vehicle__model")


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