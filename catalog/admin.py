from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "brand",
        "model",
        "offer_type",
        "availability_status",
        "price_sale",
        "price_monthly",
        "updated_at",
    )
    list_filter = (
        "offer_type",
        "availability_status",
        "fuel_type",
        "gearbox",
        "year",
    )
    search_fields = (
        "reference",
        "brand",
        "model",
        "category",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "brand",
        "model",
        "reference",
    )
    actions = (
        "set_offer_sale",
        "set_offer_lld",
        "set_offer_both",
        "set_available",
        "set_unavailable",
    )

    @admin.action(description="Basculer en achat")
    def set_offer_sale(self, request, queryset):
        queryset.update(offer_type=Vehicle.OfferType.SALE)

    @admin.action(description="Basculer en location")
    def set_offer_lld(self, request, queryset):
        queryset.update(offer_type=Vehicle.OfferType.LLD)

    @admin.action(description="Basculer en achat & location")
    def set_offer_both(self, request, queryset):
        queryset.update(offer_type=Vehicle.OfferType.BOTH)

    @admin.action(description="Marquer comme disponible")
    def set_available(self, request, queryset):
        queryset.update(availability_status=Vehicle.AvailabilityStatus.AVAILABLE)

    @admin.action(description="Marquer comme indisponible")
    def set_unavailable(self, request, queryset):
        queryset.update(availability_status=Vehicle.AvailabilityStatus.UNAVAILABLE)