from django import forms

from catalog.models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "reference",
            "brand",
            "model",
            "trim",
            "category",
            "image",
            "year",
            "mileage",
            "fuel_type",
            "gearbox",
            "color",
            "doors",
            "seats",
            "fiscal_power",
            "power_hp",
            "co2_emissions",
            "consumption",
            "crit_air",
            "warranty",
            "included_options",
            "price_sale",
            "price_monthly",
            "description",
            "offer_type",
            "availability_status",
        ]

        widgets = {
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "trim": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "year": forms.NumberInput(attrs={"class": "form-control"}),
            "mileage": forms.NumberInput(attrs={"class": "form-control"}),
            "fuel_type": forms.Select(attrs={"class": "form-select"}),
            "gearbox": forms.Select(attrs={"class": "form-select"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "doors": forms.NumberInput(attrs={"class": "form-control"}),
            "seats": forms.NumberInput(attrs={"class": "form-control"}),
            "fiscal_power": forms.NumberInput(attrs={"class": "form-control"}),
            "power_hp": forms.NumberInput(attrs={"class": "form-control"}),
            "co2_emissions": forms.NumberInput(attrs={"class": "form-control"}),
            "consumption": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                }
            ),
            "crit_air": forms.TextInput(attrs={"class": "form-control"}),
            "warranty": forms.TextInput(attrs={"class": "form-control"}),
            "included_options": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Exemple : GPS, Bluetooth, Caméra de recul, Climatisation automatique",
                }
            ),
            "price_sale": forms.NumberInput(attrs={"class": "form-control"}),
            "price_monthly": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "offer_type": forms.Select(attrs={"class": "form-select"}),
            "availability_status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        offer_type = cleaned_data.get("offer_type")
        price_sale = cleaned_data.get("price_sale")
        price_monthly = cleaned_data.get("price_monthly")

        if offer_type in [Vehicle.OfferType.SALE, Vehicle.OfferType.BOTH] and not price_sale:
            self.add_error(
                "price_sale",
                "Le prix de vente est obligatoire pour un véhicule à vendre.",
            )

        if offer_type in [Vehicle.OfferType.LLD, Vehicle.OfferType.BOTH] and not price_monthly:
            self.add_error(
                "price_monthly",
                "La mensualité est obligatoire pour un véhicule en location.",
            )

        return cleaned_data