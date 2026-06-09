from datetime import date

from django import forms

from .models import Dossier
from .models import DossierAdvisorMessage


class DossierCompletionForm(forms.ModelForm):
    class Meta:
        model = Dossier
        fields = [
            "birth_date",
            "address",
            "postal_code",
            "city",
            "housing_status",
            "monthly_rent",
            "has_current_credit",
            "monthly_credit_amount",
            "data_processing_consent",
        ]
        labels = {
            "birth_date": "Date de naissance",
            "address": "Adresse",
            "postal_code": "Code postal",
            "city": "Ville",
            "housing_status": "Situation de logement",
            "monthly_rent": "Montant du loyer mensuel",
            "has_current_credit": "Avez-vous un crédit en cours ?",
            "monthly_credit_amount": "Montant total des mensualités de crédit",
            "data_processing_consent": "J’accepte le traitement de mes données dans le cadre de ma demande.",
        }
        widgets = {
            "birth_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control finance-input",
                    "type": "date",
                },
            ),
            "address": forms.TextInput(
                    attrs={
                        "class": "form-control finance-input",
                        "placeholder": "Adresse complète",
                    }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "form-control finance-input",
                    "placeholder": "Code postal",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control finance-input",
                    "placeholder": "Ville",
                }
            ),
            "housing_status": forms.Select(
                attrs={
                    "class": "form-select finance-input"
                    }
            ),
            "monthly_rent": forms.NumberInput(
                attrs={
                    "class": "form-control finance-input",
                    "placeholder": "Exemple : 750",
                    "min": "0",
                    "step": "0.01",
                }
            ),
           "has_current_credit": forms.RadioSelect(
                choices=((True, "Oui"), (False, "Non")),
                attrs={"class": "form-check-input"},
            ),
            "monthly_credit_amount": forms.NumberInput(
                attrs={
                    "class": "form-control finance-input",
                    "placeholder": "Exemple : 250",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "data_processing_consent": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["birth_date"].input_formats = ["%Y-%m-%d"]

    def clean(self):
        cleaned_data = super().clean()

        birth_date = cleaned_data.get("birth_date")
        address = cleaned_data.get("address")
        postal_code = cleaned_data.get("postal_code")
        city = cleaned_data.get("city")
        housing_status = cleaned_data.get("housing_status")
        monthly_rent = cleaned_data.get("monthly_rent")
        has_current_credit = cleaned_data.get("has_current_credit")
        monthly_credit_amount = cleaned_data.get("monthly_credit_amount")
        data_processing_consent = cleaned_data.get("data_processing_consent")

        if birth_date is None:
            self.add_error("birth_date", "Veuillez renseigner votre date de naissance.")
        else:
            today = date.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            if age < 18:
                self.add_error(
                    "birth_date",
                    "Vous devez avoir au moins 18 ans pour déposer une demande.",
                )

        if not address:
            self.add_error("address", "Veuillez renseigner votre adresse.")

        if not postal_code:
            self.add_error("postal_code", "Veuillez renseigner votre code postal.")

        if not city:
            self.add_error("city", "Veuillez renseigner votre ville.")

        if not data_processing_consent:
            self.add_error(
                "data_processing_consent",
                "Vous devez accepter le traitement de vos données pour continuer.",
            )

        if housing_status == Dossier.HousingStatus.TENANT and monthly_rent in [None, ""]:
            self.add_error(
                "monthly_rent",
                "Veuillez renseigner le montant de votre loyer.",
            )

        if has_current_credit and monthly_credit_amount in [None, ""]:
            self.add_error(
                "monthly_credit_amount",
                "Veuillez renseigner le montant de vos mensualités de crédit.",
            )

        return cleaned_data


class DocumentUploadForm(forms.Form):
    document_type = forms.ChoiceField(
        label="Type de document",
        choices=[],
        widget=forms.HiddenInput(),
    )
    file = forms.FileField(
        label="Fichier",
        widget=forms.FileInput(attrs={"class": "form-control finance-file-input"}),
    )

    allowed_content_types = [
        "application/pdf",
        "image/jpeg",
        "image/png",
    ]
    max_file_size = 5 * 1024 * 1024

    def __init__(self, *args, allowed_document_types=None, **kwargs):
        super().__init__(*args, **kwargs)

        if allowed_document_types is None:
            allowed_document_types = []

        self.fields["document_type"].choices = allowed_document_types

    def clean_file(self):
        file = self.cleaned_data["file"]

        if file.content_type not in self.allowed_content_types:
            raise forms.ValidationError(
                "Format non autorisé. Merci d’envoyer un fichier PDF, JPG ou PNG."
            )

        if file.size > self.max_file_size:
            raise forms.ValidationError(
                "Le fichier est trop lourd. Taille maximum autorisée : 5 Mo."
            )

        return file

class DossierAdvisorMessageForm(forms.ModelForm):
    class Meta:
        model = DossierAdvisorMessage
        fields = ["subject", "message"]
        labels = {
            "subject": "Sujet",
            "message": "Votre message",
        }
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Question concernant mon dossier",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Expliquez votre demande à un conseiller M-Motors...",
                }
            ),
        }