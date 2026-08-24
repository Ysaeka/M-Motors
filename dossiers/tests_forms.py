from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from dossiers.forms import (
    DocumentUploadForm,
    DossierAdvisorMessageForm,
    DossierCompletionForm,
)
from dossiers.models import Dossier


class DossierCompletionFormTests(TestCase):
    def get_valid_form_data(self):
        return {
            "birth_date": "1990-01-01",
            "address": "10 rue de Test",
            "postal_code": "13090",
            "city": "Aix-en-Provence",
            "housing_status": Dossier.HousingStatus.TENANT,
            "monthly_rent": "750",
            "has_current_credit": "False",
            "monthly_credit_amount": "",
            "data_processing_consent": "on",
        }

    def test_completion_form_is_valid_with_required_data(self):
        form = DossierCompletionForm(data=self.get_valid_form_data())

        self.assertTrue(form.is_valid())

    def test_completion_form_rejects_underage_user(self):
        data = self.get_valid_form_data()
        today = date.today()
        data["birth_date"] = f"{today.year - 17}-01-01"

        form = DossierCompletionForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("birth_date", form.errors)

    def test_completion_form_requires_address_information(self):
        data = self.get_valid_form_data()
        data["address"] = ""
        data["postal_code"] = ""
        data["city"] = ""

        form = DossierCompletionForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("address", form.errors)
        self.assertIn("postal_code", form.errors)
        self.assertIn("city", form.errors)

    def test_completion_form_requires_consent(self):
        data = self.get_valid_form_data()
        data["data_processing_consent"] = ""

        form = DossierCompletionForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("data_processing_consent", form.errors)

    def test_completion_form_requires_rent_for_tenant(self):
        data = self.get_valid_form_data()
        data["housing_status"] = Dossier.HousingStatus.TENANT
        data["monthly_rent"] = ""

        form = DossierCompletionForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("monthly_rent", form.errors)

    def test_completion_form_requires_credit_amount_when_credit_exists(self):
        data = self.get_valid_form_data()
        data["has_current_credit"] = "True"
        data["monthly_credit_amount"] = ""

        form = DossierCompletionForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("monthly_credit_amount", form.errors)


class DocumentUploadFormTests(TestCase):
    def get_allowed_document_types(self):
        return [("identity", "Pièce d'identité")]

    def test_document_upload_form_accepts_pdf_file(self):
        uploaded_file = SimpleUploadedFile(
            "document.pdf",
            b"contenu test",
            content_type="application/pdf",
        )

        form = DocumentUploadForm(
            data={"document_type": "identity"},
            files={"file": uploaded_file},
            allowed_document_types=self.get_allowed_document_types(),
        )

        self.assertTrue(form.is_valid())

    def test_document_upload_form_rejects_invalid_file_type(self):
        uploaded_file = SimpleUploadedFile(
            "document.txt",
            b"contenu test",
            content_type="text/plain",
        )

        form = DocumentUploadForm(
            data={"document_type": "identity"},
            files={"file": uploaded_file},
            allowed_document_types=self.get_allowed_document_types(),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)

    def test_document_upload_form_rejects_file_too_large(self):
        uploaded_file = SimpleUploadedFile(
            "document.pdf",
            b"x" * (DocumentUploadForm.max_file_size + 1),
            content_type="application/pdf",
        )

        form = DocumentUploadForm(
            data={"document_type": "identity"},
            files={"file": uploaded_file},
            allowed_document_types=self.get_allowed_document_types(),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)


class DossierAdvisorMessageFormTests(TestCase):
    def test_advisor_message_form_is_valid(self):
        form = DossierAdvisorMessageForm(
            data={
                "subject": "Question dossier",
                "message": "Bonjour, je souhaite avoir une information sur mon dossier.",
            }
        )

        self.assertTrue(form.is_valid())

    def test_advisor_message_form_requires_subject_and_message(self):
        form = DossierAdvisorMessageForm(data={"subject": "", "message": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("subject", form.errors)
        self.assertIn("message", form.errors)