from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from catalog.models import Vehicle

from .models import Document, Dossier, DossierStatusHistory


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
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        response = self.client.post(
            reverse(
                "start_dossier",
                args=[
                    self.vehicle.pk,
                    Dossier.ApplicationType.SALE,
                ],
            )
        )

        dossier = Dossier.objects.get(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
        )

        self.assertRedirects(
            response,
            reverse("dossier_detail", args=[dossier.pk]),
        )
        self.assertEqual(
            dossier.status,
            Dossier.Status.DRAFT,
        )

    def test_start_dossier_requires_login(self):
        response = self.client.post(
            reverse(
                "start_dossier",
                args=[
                    self.vehicle.pk,
                    Dossier.ApplicationType.SALE,
                ],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/accounts/login/",
            response.url,
        )

    def test_start_dossier_rejects_get_request(self):
        """
        Une création de dossier modifie la base de données.
        La vue doit donc refuser une requête GET.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        response = self.client.get(
            reverse(
                "start_dossier",
                args=[
                    self.vehicle.pk,
                    Dossier.ApplicationType.SALE,
                ],
            )
        )

        self.assertEqual(response.status_code, 405)
        self.assertFalse(
            Dossier.objects.filter(
                customer=self.user,
                vehicle=self.vehicle,
            ).exists()
        )

    def test_start_dossier_reuses_existing_active_dossier(self):
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        url = reverse(
            "start_dossier",
            args=[
                self.vehicle.pk,
                Dossier.ApplicationType.SALE,
            ],
        )

        first_response = self.client.post(url)
        second_response = self.client.post(url)

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

        self.assertRedirects(
            first_response,
            reverse("dossier_detail", args=[dossier.pk]),
        )

        self.assertRedirects(
            second_response,
            reverse("dossier_detail", args=[dossier.pk]),
        )

    def test_user_can_submit_own_draft_dossier(self):
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        response = self.client.post(
            reverse(
                "submit_dossier",
                args=[dossier.pk],
            )
        )

        dossier.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("dossier_detail", args=[dossier.pk]),
        )
        self.assertEqual(
            dossier.status,
            Dossier.Status.SUBMITTED,
        )
        self.assertIsNotNone(dossier.submitted_at)

    def test_submit_dossier_rejects_get_request(self):
        """
        La soumission change le statut du dossier.
        Elle doit obligatoirement utiliser POST.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        response = self.client.get(
            reverse(
                "submit_dossier",
                args=[dossier.pk],
            )
        )

        self.assertEqual(response.status_code, 405)

        dossier.refresh_from_db()

        self.assertEqual(
            dossier.status,
            Dossier.Status.DRAFT,
        )
        self.assertIsNone(dossier.submitted_at)

    def test_user_can_delete_own_draft_dossier(self):
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        response = self.client.post(
            reverse(
                "delete_dossier",
                args=[dossier.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("accounts:espace_client"),
        )

        self.assertFalse(
            Dossier.objects.filter(
                pk=dossier.pk
            ).exists()
        )

    def test_delete_dossier_rejects_get_request(self):
        """
        La suppression d'un dossier est une action destructive.
        Une requête GET doit être refusée.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        response = self.client.get(
            reverse(
                "delete_dossier",
                args=[dossier.pk],
            )
        )

        self.assertEqual(response.status_code, 405)

        self.assertTrue(
            Dossier.objects.filter(
                pk=dossier.pk
            ).exists()
        )

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

        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        response = self.client.get(
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_access_own_document(self):
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

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

        response = self.client.get(
            reverse(
                "document_download",
                args=[document.pk],
            )
        )

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

        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        response = self.client.get(
            reverse(
                "document_download",
                args=[document.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_upload_valid_document(self):
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

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
            reverse(
                "complete_dossier",
                args=[dossier.pk],
            ),
            {
                "action": "upload_document",
                "document_type": Document.DocumentType.ID_CARD,
                "file": uploaded_file,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "complete_dossier",
                args=[dossier.pk],
            ),
        )

        self.assertTrue(
            Document.objects.filter(
                dossier=dossier,
                document_type=Document.DocumentType.ID_CARD,
            ).exists()
        )

    def test_user_cannot_upload_invalid_document_type(self):
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

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
            reverse(
                "complete_dossier",
                args=[dossier.pk],
            ),
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

        self.assertContains(
            response,
            "Format non autorisé",
        )

    def test_submitted_dossier_cannot_save_information(self):
        """
        Une fois soumis, le client ne doit plus pouvoir
        modifier les informations déclarées dans son dossier.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.SUBMITTED,
            birth_date="1990-01-01",
            address="12 rue de test",
            postal_code="75000",
            city="Paris",
            data_processing_consent=True,
        )

        response = self.client.post(
            reverse(
                "complete_dossier",
                args=[dossier.pk],
            ),
            {
                "action": "save_information",
                "birth_date": "2000-01-01",
                "address": "Adresse modifiée",
                "postal_code": "13000",
                "city": "Marseille",
                "data_processing_consent": True,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            ),
        )

        dossier.refresh_from_db()

        self.assertEqual(
            dossier.address,
            "12 rue de test",
        )
        self.assertEqual(
            dossier.city,
            "Paris",
        )

    def test_submitted_dossier_cannot_upload_new_document(self):
        """
        Après soumission, un nouveau document ne peut plus être
        ajouté librement au dossier.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.SUBMITTED,
        )

        uploaded_file = SimpleUploadedFile(
            "identity.pdf",
            b"fake pdf content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse(
                "complete_dossier",
                args=[dossier.pk],
            ),
            {
                "action": "upload_document",
                "document_type": Document.DocumentType.ID_CARD,
                "file": uploaded_file,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            ),
        )

        self.assertFalse(
            Document.objects.filter(
                dossier=dossier,
                document_type=Document.DocumentType.ID_CARD,
            ).exists()
        )

    def test_under_review_dossier_can_replace_rejected_document(self):
        """
        Un document explicitement refusé peut être remplacé
        pendant l'instruction du dossier.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.UNDER_REVIEW,
        )

        old_file = SimpleUploadedFile(
            "old_identity.pdf",
            b"old fake pdf content",
            content_type="application/pdf",
        )

        document = Document.objects.create(
            dossier=dossier,
            document_type=Document.DocumentType.ID_CARD,
            file=old_file,
            validation_status=Document.ValidationStatus.REJECTED,
            rejection_reason="Document illisible",
        )

        replacement_file = SimpleUploadedFile(
            "new_identity.pdf",
            b"new fake pdf content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse(
                "complete_dossier",
                args=[dossier.pk],
            ),
            {
                "action": "upload_document",
                "document_type": Document.DocumentType.ID_CARD,
                "file": replacement_file,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "complete_dossier",
                args=[dossier.pk],
            ),
        )

        document.refresh_from_db()
        dossier.refresh_from_db()

        self.assertEqual(
            document.validation_status,
            Document.ValidationStatus.PENDING,
        )
        self.assertEqual(
            document.rejection_reason,
            "",
        )
        self.assertEqual(
            dossier.status,
            Dossier.Status.UNDER_REVIEW,
        )

        self.assertTrue(
            DossierStatusHistory.objects.filter(
                dossier=dossier,
                new_status=Dossier.Status.UNDER_REVIEW,
            ).exists()
        )

    def test_approved_dossier_cannot_replace_document(self):
        """
        Un dossier définitivement approuvé ne doit plus
        pouvoir être modifié par le client.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.APPROVED,
        )

        old_file = SimpleUploadedFile(
            "old_identity.pdf",
            b"old fake pdf content",
            content_type="application/pdf",
        )

        document = Document.objects.create(
            dossier=dossier,
            document_type=Document.DocumentType.ID_CARD,
            file=old_file,
            validation_status=Document.ValidationStatus.REJECTED,
        )

        original_file_name = document.file.name

        replacement_file = SimpleUploadedFile(
            "new_identity.pdf",
            b"new fake pdf content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse(
                "complete_dossier",
                args=[dossier.pk],
            ),
            {
                "action": "upload_document",
                "document_type": Document.DocumentType.ID_CARD,
                "file": replacement_file,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            ),
        )

        document.refresh_from_db()

        self.assertEqual(
            document.file.name,
            original_file_name,
        )
        self.assertEqual(
            document.validation_status,
            Document.ValidationStatus.REJECTED,
        )

    def test_user_can_save_lld_duration(self):
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.LLD,
            status=Dossier.Status.DRAFT,
        )

        response = self.client.post(
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            ),
            {
                "lld_duration_months": 48,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            ),
        )

        dossier.refresh_from_db()

        self.assertEqual(
            dossier.lld_duration_months,
            48,
        )

    def test_submitted_dossier_cannot_change_lld_duration(self):
        """
        La durée d'une LLD ne peut plus être changée
        après soumission du dossier.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.LLD,
            status=Dossier.Status.SUBMITTED,
            lld_duration_months=36,
        )

        response = self.client.post(
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            ),
            {
                "lld_duration_months": 48,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            ),
        )

        dossier.refresh_from_db()

        self.assertEqual(
            dossier.lld_duration_months,
            36,
        )

    def test_submitting_dossier_reserves_vehicle(self):
        """
        La soumission d'un dossier doit réserver immédiatement
        le véhicule associé.
        """
        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        response = self.client.post(
            reverse(
                "submit_dossier",
                args=[dossier.pk],
            )
        )

        dossier.refresh_from_db()
        self.vehicle.refresh_from_db()

        self.assertRedirects(
            response,
            reverse(
                "dossier_detail",
                args=[dossier.pk],
            ),
        )

        self.assertEqual(
            dossier.status,
            Dossier.Status.SUBMITTED,
        )

        self.assertEqual(
            self.vehicle.availability_status,
            Vehicle.AvailabilityStatus.RESERVED,
        )


    def test_second_client_cannot_submit_dossier_for_reserved_vehicle(self):
        """
        Si deux clients possèdent un brouillon pour le même véhicule,
        seul le premier qui soumet peut réserver le véhicule.
        """
        User = get_user_model()

        second_user = User.objects.create_user(
            username="secondclient",
            email="secondclient@example.com",
            password="Testpass123!",
        )

        first_dossier = Dossier.objects.create(
            customer=self.user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        second_dossier = Dossier.objects.create(
            customer=second_user,
            vehicle=self.vehicle,
            application_type=Dossier.ApplicationType.SALE,
            status=Dossier.Status.DRAFT,
        )

        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        first_response = self.client.post(
            reverse(
                "submit_dossier",
                args=[first_dossier.pk],
            )
        )

        first_dossier.refresh_from_db()
        self.vehicle.refresh_from_db()

        self.assertRedirects(
            first_response,
            reverse(
                "dossier_detail",
                args=[first_dossier.pk],
            ),
        )

        self.assertEqual(
            first_dossier.status,
            Dossier.Status.SUBMITTED,
        )

        self.assertEqual(
            self.vehicle.availability_status,
            Vehicle.AvailabilityStatus.RESERVED,
        )

        self.client.logout()

        self.client.login(
            username="secondclient",
            password="Testpass123!",
        )

        second_response = self.client.post(
            reverse(
                "submit_dossier",
                args=[second_dossier.pk],
            )
        )

        second_dossier.refresh_from_db()
        self.vehicle.refresh_from_db()

        self.assertRedirects(
            second_response,
            reverse(
                "vehicle_detail",
                args=[self.vehicle.pk],
            ),
        )

        self.assertEqual(
            second_dossier.status,
            Dossier.Status.DRAFT,
        )

        self.assertIsNone(
            second_dossier.submitted_at,
        )

        self.assertEqual(
            self.vehicle.availability_status,
            Vehicle.AvailabilityStatus.RESERVED,
        )


    def test_user_cannot_start_dossier_for_unavailable_vehicle(self):
        """
        Aucun nouveau dossier ne doit pouvoir être créé
        pour un véhicule déjà réservé.
        """
        self.vehicle.availability_status = (
            Vehicle.AvailabilityStatus.RESERVED
        )

        self.vehicle.save(
            update_fields=[
                "availability_status",
                "updated_at",
            ]
        )

        self.client.login(
            username="clienttest",
            password="Testpass123!",
        )

        response = self.client.post(
            reverse(
                "start_dossier",
                args=[
                    self.vehicle.pk,
                    Dossier.ApplicationType.SALE,
                ],
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "vehicle_detail",
                args=[self.vehicle.pk],
            ),
        )

        self.assertFalse(
            Dossier.objects.filter(
                customer=self.user,
                vehicle=self.vehicle,
            ).exists()
        )