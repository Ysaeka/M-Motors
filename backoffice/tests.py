from django.test import TestCase

from backoffice.forms import VehicleForm
from catalog.models import Vehicle


class VehicleFormTests(TestCase):
    def get_valid_form_data(self):
        return {
            "reference": "TEST-001",
            "brand": "Renault",
            "model": "Clio",
            "trim": "Intens",
            "category": "Citadine",
            "year": 2022,
            "mileage": 25000,
            "fuel_type": Vehicle.FuelType.GASOLINE,
            "gearbox": Vehicle.GearboxType.MANUAL,
            "color": "Blanc",
            "doors": 5,
            "seats": 5,
            "fiscal_power": 5,
            "power_hp": 90,
            "co2_emissions": 120,
            "consumption": "5.4",
            "crit_air": "Crit'Air 1",
            "warranty": "12 mois",
            "included_options": "GPS, Bluetooth, Caméra de recul",
            "price_sale": "15000",
            "price_monthly": "250",
            "description": "Véhicule de test",
            "offer_type": Vehicle.OfferType.BOTH,
            "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
        }

    def test_vehicle_form_is_valid_with_sale_and_lld_prices(self):
        form = VehicleForm(data=self.get_valid_form_data())

        self.assertTrue(form.is_valid())

    def test_vehicle_form_requires_sale_price_for_sale_offer(self):
        data = self.get_valid_form_data()
        data["offer_type"] = Vehicle.OfferType.SALE
        data["price_sale"] = ""

        form = VehicleForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("price_sale", form.errors)

    def test_vehicle_form_requires_monthly_price_for_lld_offer(self):
        data = self.get_valid_form_data()
        data["offer_type"] = Vehicle.OfferType.LLD
        data["price_monthly"] = ""

        form = VehicleForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("price_monthly", form.errors)

    def test_vehicle_form_requires_both_prices_for_mixed_offer(self):
        data = self.get_valid_form_data()
        data["offer_type"] = Vehicle.OfferType.BOTH
        data["price_sale"] = ""
        data["price_monthly"] = ""

        form = VehicleForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("price_sale", form.errors)
        self.assertIn("price_monthly", form.errors)