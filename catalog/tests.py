from django.test import TestCase
from django.urls import reverse

from .models import Vehicle


class CatalogViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vehicle_sale = Vehicle.objects.create(
            reference="TEST-SALE-001",
            brand="Peugeot",
            model="208",
            trim="Allure",
            category="Citadine",
            year=2021,
            mileage=35000,
            fuel_type=Vehicle.FuelType.GASOLINE,
            gearbox=Vehicle.GearboxType.MANUAL,
            price_sale=14990.00,
            price_monthly=None,
            description="Véhicule achat de test",
            offer_type=Vehicle.OfferType.SALE,
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE,
        )

        cls.vehicle_lld = Vehicle.objects.create(
            reference="TEST-LLD-001",
            brand="Renault",
            model="Clio",
            trim="Business",
            category="Citadine",
            year=2022,
            mileage=18000,
            fuel_type=Vehicle.FuelType.HYBRID,
            gearbox=Vehicle.GearboxType.AUTOMATIC,
            price_sale=None,
            price_monthly=299.00,
            description="Véhicule location de test",
            offer_type=Vehicle.OfferType.LLD,
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE,
        )

    def test_vehicle_list_returns_200(self):
        response = self.client.get(reverse("vehicle_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/vehicle_list.html")

    def test_vehicle_list_displays_vehicles(self):
        response = self.client.get(reverse("vehicle_list"))

        self.assertContains(response, "Peugeot 208 2021")
        self.assertContains(response, "Renault Clio 2022")

    def test_vehicle_detail_returns_200(self):
        response = self.client.get(reverse("vehicle_detail", args=[self.vehicle_sale.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/vehicle_detail.html")

    def test_vehicle_detail_displays_vehicle_data(self):
        response = self.client.get(reverse("vehicle_detail", args=[self.vehicle_sale.pk]))

        self.assertContains(response, "Peugeot")
        self.assertContains(response, "208")

    def test_vehicle_list_filter_by_offer_type_sale(self):
        response = self.client.get(reverse("vehicle_list"), {"offer_type": "sale"})

        self.assertContains(response, "Peugeot 208 2021")
        self.assertContains(response, "14&nbsp;990 €", html=True)
        self.assertNotContains(response, "Renault Clio 2022")

    def test_vehicle_list_filter_by_offer_type_lld(self):
        response = self.client.get(reverse("vehicle_list"), {"offer_type": "lld"})

        self.assertContains(response, "Renault Clio 2022")
        self.assertContains(response, "299 €/mois")
        self.assertNotContains(response, "Peugeot 208 2021")

    def test_vehicle_references_are_hidden_for_public_users(self):
        response = self.client.get(reverse("vehicle_list"))

        self.assertNotContains(response, "TEST-SALE-001")
        self.assertNotContains(response, "TEST-LLD-001")

    def test_vehicle_list_sort_by_sale_price_ascending(self):
        Vehicle.objects.create(
            reference="TEST-SALE-LOW",
            brand="Citroën",
            model="C3",
            year=2020,
            mileage=40000,
            fuel_type=Vehicle.FuelType.GASOLINE,
            gearbox=Vehicle.GearboxType.MANUAL,
            price_sale=12000.00,
            price_monthly=None,
            offer_type=Vehicle.OfferType.SALE,
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE,
        )

        response = self.client.get(
            reverse("vehicle_list"),
            {"sort": "price_sale_asc"},
        )

        vehicles = list(response.context["vehicles"].object_list)

        self.assertEqual(vehicles[0].reference, "TEST-SALE-LOW")
        self.assertEqual(response.context["selected_sort"], "price_sale_asc")

    def test_vehicle_list_sort_by_sale_price_descending(self):
        Vehicle.objects.create(
            reference="TEST-SALE-HIGH",
            brand="BMW",
            model="Serie 1",
            year=2023,
            mileage=12000,
            fuel_type=Vehicle.FuelType.GASOLINE,
            gearbox=Vehicle.GearboxType.AUTOMATIC,
            price_sale=30000.00,
            price_monthly=None,
            offer_type=Vehicle.OfferType.SALE,
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE,
        )

        response = self.client.get(
            reverse("vehicle_list"),
            {"sort": "price_sale_desc"},
        )

        vehicles = list(response.context["vehicles"].object_list)

        self.assertEqual(vehicles[0].reference, "TEST-SALE-HIGH")
        self.assertEqual(response.context["selected_sort"], "price_sale_desc")

    def test_vehicle_list_sort_by_monthly_price_ascending(self):
        Vehicle.objects.create(
            reference="TEST-LLD-LOW",
            brand="Toyota",
            model="Yaris",
            year=2023,
            mileage=10000,
            fuel_type=Vehicle.FuelType.HYBRID,
            gearbox=Vehicle.GearboxType.AUTOMATIC,
            price_sale=None,
            price_monthly=199.00,
            offer_type=Vehicle.OfferType.LLD,
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE,
        )

        response = self.client.get(
            reverse("vehicle_list"),
            {"sort": "price_monthly_asc"},
        )

        vehicles = list(response.context["vehicles"].object_list)

        self.assertEqual(vehicles[0].reference, "TEST-LLD-LOW")
        self.assertEqual(response.context["selected_sort"], "price_monthly_asc")

    def test_vehicle_list_invalid_sort_falls_back_to_newest(self):
        response = self.client.get(
            reverse("vehicle_list"),
            {"sort": "unknown"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_sort"], "newest")


class VehicleModelTests(TestCase):
    def test_vehicle_str_returns_brand_model_and_reference(self):
        vehicle = Vehicle.objects.create(
            reference="MODEL-001",
            brand="BMW",
            model="Serie 1",
            trim="M Sport",
            category="Compacte",
            year=2020,
            mileage=42000,
            fuel_type=Vehicle.FuelType.DIESEL,
            gearbox=Vehicle.GearboxType.AUTOMATIC,
            price_sale=21990.00,
            price_monthly=None,
            description="Véhicule de test modèle",
            offer_type=Vehicle.OfferType.SALE,
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE,
        )

        self.assertEqual(str(vehicle), "BMW Serie 1 (MODEL-001)")

    def test_vehicle_default_availability_status_is_available(self):
        vehicle = Vehicle.objects.create(
            reference="MODEL-002",
            brand="Audi",
            model="A3",
            trim="S line",
            category="Compacte",
            year=2021,
            mileage=25000,
            fuel_type=Vehicle.FuelType.GASOLINE,
            gearbox=Vehicle.GearboxType.MANUAL,
            price_sale=24990.00,
            price_monthly=None,
            description="Véhicule de test disponibilité",
            offer_type=Vehicle.OfferType.SALE,
        )

        self.assertEqual(
            vehicle.availability_status,
            Vehicle.AvailabilityStatus.AVAILABLE,
        )