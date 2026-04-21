# Register your models here.

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
    )
    list_filter = ("offer_type", "availability_status", "fuel_type", "gearbox")
    search_fields = ("reference", "brand", "model")