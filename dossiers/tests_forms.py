from datetime import date
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from pypdf import PdfWriter

from dossiers.forms import (
    DocumentUploadForm,
    DossierAdvisorMessageForm,
    DossierCompletionForm,
)
from dossiers.models import Dossier


def create_valid_pdf():
    """
    Génère un petit fichier PDF réellement valide en mémoire.
    """
    buffer = BytesIO()

    writer = PdfWriter()
    writer.add_blank_page(
        width=72,
        height=72,
    )
    writer.write(buffer)

    return buffer.getvalue()


def create_valid_image(image_format="PNG"):
    """
    Génère une petite image réellement valide en mémoire.
    """
    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (10, 10),
    )
    image.save(
        buffer,
        format=image_format,
    )

    return buffer.getvalue()


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
        form = DossierCompletionForm(
            data=self.get_valid_form_data()
        )

        self.assertTrue(form.is_valid())

    def test_completion_form_rejects_underage_user(self):
        data = self.get_valid_form_data()
        today = date.today()

        data["birth_date"] = (
            f"{today.year - 17}-01-01"
        )

        form = DossierCompletionForm(
            data=data
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "birth_date",
            form.errors,
        )

    def test_completion_form_requires_address_information(self):
        data = self.get_valid_form_data()

        data["address"] = ""
        data["postal_code"] = ""
        data["city"] = ""

        form = DossierCompletionForm(
            data=data
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "address",
            form.errors,
        )

        self.assertIn(
            "postal_code",
            form.errors,
        )

        self.assertIn(
            "city",
            form.errors,
        )

    def test_completion_form_requires_consent(self):
        data = self.get_valid_form_data()
        data["data_processing_consent"] = ""

        form = DossierCompletionForm(
            data=data
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "data_processing_consent",
            form.errors,
        )

    def test_completion_form_requires_rent_for_tenant(self):
        data = self.get_valid_form_data()

        data["housing_status"] = (
            Dossier.HousingStatus.TENANT
        )
        data["monthly_rent"] = ""

        form = DossierCompletionForm(
            data=data
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "monthly_rent",
            form.errors,
        )

    def test_completion_form_requires_credit_amount_when_credit_exists(
        self,
    ):
        data = self.get_valid_form_data()

        data["has_current_credit"] = "True"
        data["monthly_credit_amount"] = ""

        form = DossierCompletionForm(
            data=data
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "monthly_credit_amount",
            form.errors,
        )


class DocumentUploadFormTests(TestCase):
    def get_allowed_document_types(self):
        return [
            (
                "identity",
                "Pièce d'identité",
            )
        ]

    def build_form(self, uploaded_file):
        return DocumentUploadForm(
            data={
                "document_type": "identity",
            },
            files={
                "file": uploaded_file,
            },
            allowed_document_types=(
                self.get_allowed_document_types()
            ),
        )

    def test_document_upload_form_accepts_valid_pdf(self):
        uploaded_file = SimpleUploadedFile(
            "document.pdf",
            create_valid_pdf(),
            content_type="application/pdf",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

    def test_document_upload_form_accepts_valid_png(self):
        uploaded_file = SimpleUploadedFile(
            "document.png",
            create_valid_image("PNG"),
            content_type="image/png",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

    def test_document_upload_form_accepts_valid_jpeg(self):
        uploaded_file = SimpleUploadedFile(
            "document.jpg",
            create_valid_image("JPEG"),
            content_type="image/jpeg",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

    def test_document_upload_form_rejects_fake_pdf(self):
        """
        Un content_type application/pdf ne doit pas suffire
        si le contenu réel n'est pas un PDF.
        """
        uploaded_file = SimpleUploadedFile(
            "document.pdf",
            b"ceci n'est pas un vrai fichier PDF",
            content_type="application/pdf",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "file",
            form.errors,
        )

    def test_document_upload_form_rejects_fake_jpeg(self):
        """
        Un content_type image/jpeg ne doit pas suffire
        si le contenu réel n'est pas une image.
        """
        uploaded_file = SimpleUploadedFile(
            "document.jpg",
            b"ceci n'est pas une vraie image",
            content_type="image/jpeg",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "file",
            form.errors,
        )

    def test_document_upload_form_rejects_fake_png(self):
        uploaded_file = SimpleUploadedFile(
            "document.png",
            b"ceci n'est pas une vraie image PNG",
            content_type="image/png",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "file",
            form.errors,
        )

    def test_document_upload_form_rejects_content_extension_mismatch(
        self,
    ):
        """
        Une vraie image PNG renommée en JPG doit être refusée.
        """
        uploaded_file = SimpleUploadedFile(
            "document.jpg",
            create_valid_image("PNG"),
            content_type="image/jpeg",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "file",
            form.errors,
        )

    def test_document_upload_form_rejects_invalid_extension(self):
        uploaded_file = SimpleUploadedFile(
            "document.txt",
            b"contenu test",
            content_type="text/plain",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "file",
            form.errors,
        )

    def test_document_upload_form_rejects_file_too_large(self):
        uploaded_file = SimpleUploadedFile(
            "document.pdf",
            b"x" * (
                DocumentUploadForm.max_file_size
                + 1
            ),
            content_type="application/pdf",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "file",
            form.errors,
        )

    def test_document_upload_form_rejects_empty_file(self):
        uploaded_file = SimpleUploadedFile(
            "document.pdf",
            b"",
            content_type="application/pdf",
        )

        form = self.build_form(
            uploaded_file
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "file",
            form.errors,
        )


class DossierAdvisorMessageFormTests(TestCase):
    def test_advisor_message_form_is_valid(self):
        form = DossierAdvisorMessageForm(
            data={
                "subject": "Question dossier",
                "message": (
                    "Bonjour, je souhaite avoir "
                    "une information sur mon dossier."
                ),
            }
        )

        self.assertTrue(
            form.is_valid()
        )

    def test_advisor_message_form_requires_subject_and_message(self):
        form = DossierAdvisorMessageForm(
            data={
                "subject": "",
                "message": "",
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "subject",
            form.errors,
        )

        self.assertIn(
            "message",
            form.errors,
        )