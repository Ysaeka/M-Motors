from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Vehicle
from dossiers.models import Dossier, DossierStatusHistory

from backoffice.forms import VehicleForm


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
        form = VehicleForm(
            data=self.get_valid_form_data()
        )

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


class DossierVehicleStatusTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.admin = User.objects.create_superuser(
            username="adminbackoffice",
            email="admin@example.com",
            password="Testpass123!",
        )

        # Pas d'adresse email pour éviter tout envoi réel
        # pendant les tests de changement de statut.
        cls.customer = User.objects.create_user(
            username="clientbackoffice",
            email="",
            password="Testpass123!",
        )

    def setUp(self):
        self.client.login(
            username="adminbackoffice",
            password="Testpass123!",
        )

    def create_vehicle(
        self,
        reference,
        availability_status=Vehicle.AvailabilityStatus.RESERVED,
    ):
        return Vehicle.objects.create(
            reference=reference,
            brand="Peugeot",
            model="5008",
            trim="Allure",
            category="Familiale",
            year=2022,
            mileage=30000,
            fuel_type=Vehicle.FuelType.DIESEL,
            gearbox=Vehicle.GearboxType.AUTOMATIC,
            price_sale=30000,
            price_monthly=350,
            description="Véhicule de test",
            offer_type=Vehicle.OfferType.BOTH,
            availability_status=availability_status,
        )

    def create_dossier(
        self,
        vehicle,
        application_type,
        status=Dossier.Status.SUBMITTED,
    ):
        return Dossier.objects.create(
            customer=self.customer,
            vehicle=vehicle,
            application_type=application_type,
            status=status,
        )

    def test_mark_under_review_keeps_vehicle_reserved(self):
        vehicle = self.create_vehicle(
            reference="STATUS-001",
        )

        dossier = self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.SALE,
        )

        response = self.client.post(
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
            {
                "action": "mark_under_review",
            },
        )

        dossier.refresh_from_db()
        vehicle.refresh_from_db()

        self.assertRedirects(
            response,
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
        )

        self.assertEqual(
            dossier.status,
            Dossier.Status.UNDER_REVIEW,
        )

        self.assertEqual(
            vehicle.availability_status,
            Vehicle.AvailabilityStatus.RESERVED,
        )

    def test_approved_sale_dossier_marks_vehicle_as_sold(self):
        vehicle = self.create_vehicle(
            reference="STATUS-002",
        )

        dossier = self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.UNDER_REVIEW,
        )

        response = self.client.post(
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
            {
                "action": "approve",
            },
        )

        dossier.refresh_from_db()
        vehicle.refresh_from_db()

        self.assertRedirects(
            response,
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
        )

        self.assertEqual(
            dossier.status,
            Dossier.Status.APPROVED,
        )

        self.assertEqual(
            vehicle.availability_status,
            Vehicle.AvailabilityStatus.SOLD,
        )

    def test_approved_lld_dossier_marks_vehicle_as_rented(self):
        vehicle = self.create_vehicle(
            reference="STATUS-003",
        )

        dossier = self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.LLD,
            status=Dossier.Status.UNDER_REVIEW,
        )

        response = self.client.post(
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
            {
                "action": "approve",
            },
        )

        dossier.refresh_from_db()
        vehicle.refresh_from_db()

        self.assertRedirects(
            response,
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
        )

        self.assertEqual(
            dossier.status,
            Dossier.Status.APPROVED,
        )

        self.assertEqual(
            vehicle.availability_status,
            Vehicle.AvailabilityStatus.RENTED,
        )

    def test_rejected_dossier_makes_vehicle_available_again(self):
        vehicle = self.create_vehicle(
            reference="STATUS-004",
        )

        dossier = self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.UNDER_REVIEW,
        )

        response = self.client.post(
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
            {
                "action": "reject",
            },
        )

        dossier.refresh_from_db()
        vehicle.refresh_from_db()

        self.assertRedirects(
            response,
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
        )

        self.assertEqual(
            dossier.status,
            Dossier.Status.REJECTED,
        )

        self.assertEqual(
            vehicle.availability_status,
            Vehicle.AvailabilityStatus.AVAILABLE,
        )

    def test_rejected_dossier_keeps_vehicle_reserved_if_another_active_dossier_exists(
        self,
    ):
        vehicle = self.create_vehicle(
            reference="STATUS-005",
        )

        rejected_dossier = self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.UNDER_REVIEW,
        )

        self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.LLD,
            status=Dossier.Status.SUBMITTED,
        )

        response = self.client.post(
            reverse(
                "backoffice:dossier_detail",
                args=[rejected_dossier.pk],
            ),
            {
                "action": "reject",
            },
        )

        rejected_dossier.refresh_from_db()
        vehicle.refresh_from_db()

        self.assertRedirects(
            response,
            reverse(
                "backoffice:dossier_detail",
                args=[rejected_dossier.pk],
            ),
        )

        self.assertEqual(
            rejected_dossier.status,
            Dossier.Status.REJECTED,
        )

        self.assertEqual(
            vehicle.availability_status,
            Vehicle.AvailabilityStatus.RESERVED,
        )

    def test_rejecting_old_dossier_does_not_reopen_sold_vehicle(self):
        vehicle = self.create_vehicle(
            reference="STATUS-006",
            availability_status=Vehicle.AvailabilityStatus.SOLD,
        )

        rejected_dossier = self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.LLD,
            status=Dossier.Status.UNDER_REVIEW,
        )

        self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.APPROVED,
        )

        response = self.client.post(
            reverse(
                "backoffice:dossier_detail",
                args=[rejected_dossier.pk],
            ),
            {
                "action": "reject",
            },
        )

        vehicle.refresh_from_db()

        self.assertRedirects(
            response,
            reverse(
                "backoffice:dossier_detail",
                args=[rejected_dossier.pk],
            ),
        )

        self.assertEqual(
            vehicle.availability_status,
            Vehicle.AvailabilityStatus.SOLD,
        )

    def test_status_change_is_added_to_history(self):
        vehicle = self.create_vehicle(
            reference="STATUS-007",
        )

        dossier = self.create_dossier(
            vehicle=vehicle,
            application_type=Dossier.ApplicationType.SALE,
        )

        self.client.post(
            reverse(
                "backoffice:dossier_detail",
                args=[dossier.pk],
            ),
            {
                "action": "mark_under_review",
            },
        )

        self.assertTrue(
            DossierStatusHistory.objects.filter(
                dossier=dossier,
                old_status=Dossier.Status.SUBMITTED,
                new_status=Dossier.Status.UNDER_REVIEW,
                changed_by=self.admin,
            ).exists()
        )