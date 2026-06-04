from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from catalog.models import Vehicle

from .models import Document, Dossier


class DossierRequestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.user = User.objects.create_user(
            username="clienttest",
            email="client@example.com",
            password="Testpass123!",
        )

        cls.vehicle = Vehicle.objects.create(
            reference="DOS-TEST-001",
            brand="Peugeot",
            model="5008",
            trim="Allure",
            category="Familiale",
            year=2021,
            mileage=45000,
            fuel_type=Vehicle.FuelType.DIESEL,
            gearbox=Vehicle.GearboxType.AUTOMATIC,
            price_sale=24900.00,
            price_monthly=219.00,
            description="Véhicule de test dossier",
            offer_type=Vehicle.OfferType.BOTH,
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE,
        )

    def test_logged_user_can_start_sale_dossier(self):
        self.client.login(username="clienttest", password="Testpass123!")

        response = self.client.get(
            reverse("start_dossier", args=[self.vehicle.pk, Dossier.ApplicationType.SALE])
        )

        dossier = Dossier.objects.get(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
        )

        self.assertRedirects(response, reverse("dossier_detail", args=[dossier.pk]))
        self.assertEqual(dossier.status, Dossier.Status.DRAFT)

    def test_start_dossier_requires_login(self):
        response = self.client.get(
            reverse("start_dossier", args=[self.vehicle.pk, Dossier.ApplicationType.SALE])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
    
    def test_start_dossier_reuses_existing_active_dossier(self):
        self.client.login(username="clienttest", password="Testpass123!")

        first_response = self.client.get(
            reverse("start_dossier", args=[self.vehicle.pk, Dossier.ApplicationType.SALE])
        )
        second_response = self.client.get(
            reverse("start_dossier", args=[self.vehicle.pk, Dossier.ApplicationType.SALE])
        )

        dossiers_count = Dossier.objects.filter(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
        ).count()

        dossier = Dossier.objects.get(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
        )

        self.assertEqual(dossiers_count, 1)
        self.assertRedirects(first_response, reverse("dossier_detail", args=[dossier.pk]))
        self.assertRedirects(second_response, reverse("dossier_detail", args=[dossier.pk]))

    def test_user_can_submit_own_draft_dossier(self):
        self.client.login(username="clienttest", password="Testpass123!")

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        response = self.client.post(reverse("submit_dossier", args=[dossier.pk]))

        dossier.refresh_from_db()

        self.assertRedirects(response, reverse("dossier_detail", args=[dossier.pk]))
        self.assertEqual(dossier.status, Dossier.Status.SUBMITTED)
        self.assertIsNotNone(dossier.submitted_at)
    
    def test_user_can_delete_own_draft_dossier(self):
        self.client.login(username="clienttest", password="Testpass123!")

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        response = self.client.post(reverse("delete_dossier", args=[dossier.pk]))

        self.assertRedirects(response, reverse("accounts:espace_client"))
        self.assertFalse(Dossier.objects.filter(pk=dossier.pk).exists())
    
    def test_user_cannot_access_another_user_dossier(self):
        User = get_user_model()
        other_user = User.objects.create_user(
            username="otherclient",
            email="other@example.com",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=other_user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        self.client.login(username="clienttest", password="Testpass123!")

        response = self.client.get(reverse("dossier_detail", args=[dossier.pk]))

        self.assertEqual(response.status_code, 404)

    def test_user_can_access_own_document(self):
        self.client.login(username="clienttest", password="Testpass123!")

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        uploaded_file = SimpleUploadedFile(
            "identity.pdf",
            b"fake pdf content",
            content_type="application/pdf",
        )

        document = Document.objects.create(
            dossier=dossier,
            document_type=Document.DocumentType.ID_CARD,
            file=uploaded_file,
        )

        response = self.client.get(reverse("document_download", args=[document.pk]))

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_access_another_user_document(self):
        User = get_user_model()
        other_user = User.objects.create_user(
            username="otherclientdoc",
            email="otherdoc@example.com",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=other_user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        uploaded_file = SimpleUploadedFile(
            "identity.pdf",
            b"fake pdf content",
            content_type="application/pdf",
        )

        document = Document.objects.create(
            dossier=dossier,
            document_type=Document.DocumentType.ID_CARD,
            file=uploaded_file,
        )

        self.client.login(username="clienttest", password="Testpass123!")

        response = self.client.get(reverse("document_download", args=[document.pk]))

        self.assertEqual(response.status_code, 404)

    def test_user_can_upload_valid_document(self):
        self.client.login(username="clienttest", password="Testpass123!")

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
            birth_date="1990-01-01",
            address="12 rue de test",
            postal_code="75000",
            city="Paris",
            data_processing_consent=True,
        )

        uploaded_file = SimpleUploadedFile(
            "identity.pdf",
            b"fake pdf content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("complete_dossier", args=[dossier.pk]),
            {
                "action": "upload_document",
                "document_type": Document.DocumentType.ID_CARD,
                "file": uploaded_file,
            },
        )

        self.assertRedirects(response, reverse("complete_dossier", args=[dossier.pk]))
        self.assertTrue(
            Document.objects.filter(
                dossier=dossier,
                document_type=Document.DocumentType.ID_CARD,
            ).exists()
        )

    def test_user_cannot_upload_invalid_document_type(self):
        self.client.login(username="clienttest", password="Testpass123!")

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
            birth_date="1990-01-01",
            address="12 rue de test",
            postal_code="75000",
            city="Paris",
            data_processing_consent=True,
        )

        uploaded_file = SimpleUploadedFile(
            "identity.txt",
            b"invalid text content",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse("complete_dossier", args=[dossier.pk]),
            {
                "action": "upload_document",
                "document_type": Document.DocumentType.ID_CARD,
                "file": uploaded_file,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Document.objects.filter(
                dossier=dossier,
                document_type=Document.DocumentType.ID_CARD,
            ).exists()
        )
        self.assertContains(response, "Format non autorisé")