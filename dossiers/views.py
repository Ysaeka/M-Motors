from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import ClientProfile
from catalog.models import Vehicle

from .forms import (
    DocumentUploadForm,
    DossierAdvisorMessageForm,
    DossierCompletionForm,
)
from .models import Document, Dossier, DossierStatusHistory, Option


# Statuts considérés comme actifs pour éviter de créer plusieurs dossiers
# en cours pour le même client, le même véhicule et le même type de demande.
ACTIVE_DOSSIER_STATUSES = [
    Dossier.Status.DRAFT,
    Dossier.Status.SUBMITTED,
    Dossier.Status.UNDER_REVIEW,
]


# Les justificatifs attendus dépendent du type de demande.
# Une LLD nécessite plus de pièces qu'une demande d'achat classique.
REQUIRED_DOCUMENTS_BY_APPLICATION_TYPE = {
    Dossier.ApplicationType.SALE: [
        Document.DocumentType.ID_CARD,
        Document.DocumentType.DRIVER_LICENSE,
        Document.DocumentType.PROOF_OF_ADDRESS,
    ],
    Dossier.ApplicationType.LLD: [
        Document.DocumentType.ID_CARD,
        Document.DocumentType.DRIVER_LICENSE,
        Document.DocumentType.PROOF_OF_ADDRESS,
        Document.DocumentType.PROOF_OF_INCOME,
        Document.DocumentType.TAX_NOTICE,
        Document.DocumentType.RENT_RECEIPT,
    ],
}


def can_replace_rejected_document(dossier, document_type):
    """
    Vérifie si le client peut remplacer un document refusé.

    Après soumission, le dossier n'est plus librement modifiable.
    La seule exception concerne un document explicitement refusé
    par le back-office pendant l'étude du dossier.
    """
    if dossier.status not in [
        Dossier.Status.SUBMITTED,
        Dossier.Status.UNDER_REVIEW,
    ]:
        return False

    return dossier.documents.filter(
        document_type=document_type,
        validation_status=Document.ValidationStatus.REJECTED,
    ).exists()


"""Affiche la liste des dossiers appartenant au client connecté."""


@login_required
def dossier_list(request):
    dossiers = (
        Dossier.objects.filter(customer=request.user)
        .select_related("vehicle")
        .order_by("-created_at")
    )

    return render(
        request,
        "dossiers/dossier_list.html",
        {
            "dossiers": dossiers,
        },
    )


"""Affiche le détail d'un dossier client et permet l'échange avec un conseiller."""


@login_required
def dossier_detail(request, pk):
    dossier = get_object_or_404(
        Dossier.objects.select_related("vehicle", "customer").prefetch_related(
            "options",
            "documents",
            "status_history",
            "advisor_messages",
        ),
        pk=pk,
        customer=request.user,
    )

    lld_included_options = Option.objects.none()
    vehicle_monthly_price = dossier.vehicle.price_monthly or Decimal("0")
    estimated_location_total = Decimal("0")
    purchase_option_estimate = None

    advisor_message_form = DossierAdvisorMessageForm(
        initial={
            "subject": f"Question concernant mon dossier #{dossier.id}",
        }
    )

    # L'envoi d'un message au conseiller reste possible
    # quel que soit le statut du dossier.
    if request.method == "POST" and "advisor_message_submit" in request.POST:
        advisor_message_form = DossierAdvisorMessageForm(request.POST)

        if advisor_message_form.is_valid():
            advisor_message = advisor_message_form.save(commit=False)
            advisor_message.dossier = dossier
            advisor_message.customer = request.user
            advisor_message.save()

            return redirect("dossier_detail", pk=dossier.pk)

    # Les options affichées pour la LLD sont incluses dans l'offre.
    # Elles servent à informer le client, sans recalcul tarifaire supplémentaire.
    if dossier.application_type == Dossier.ApplicationType.LLD:
        lld_included_options = Option.objects.filter(
            is_active=True
        ).order_by("name")

        if request.method == "POST" and "lld_duration_months" in request.POST:
            # La durée LLD ne peut être modifiée
            # que tant que le dossier est en brouillon.
            if dossier.status != Dossier.Status.DRAFT:
                return redirect("dossier_detail", pk=dossier.pk)

            lld_duration_months = request.POST.get("lld_duration_months")
            valid_durations = [
                choice[0] for choice in Dossier.LLDDuration.choices
            ]

            if lld_duration_months:
                lld_duration_months = int(lld_duration_months)

                if lld_duration_months in valid_durations:
                    dossier.lld_duration_months = lld_duration_months
                    dossier.save(update_fields=["lld_duration_months"])

            return redirect("dossier_detail", pk=dossier.pk)

        if dossier.lld_duration_months:
            estimated_location_total = (
                vehicle_monthly_price * dossier.lld_duration_months
            )

            if dossier.vehicle.price_sale:
                purchase_option_estimate = (
                    dossier.vehicle.price_sale - estimated_location_total
                )

                if purchase_option_estimate < 0:
                    purchase_option_estimate = Decimal("0")

    return render(
        request,
        "dossiers/dossier_detail.html",
        {
            "dossier": dossier,
            "lld_included_options": lld_included_options,
            "vehicle_monthly_price": vehicle_monthly_price,
            "estimated_location_total": estimated_location_total,
            "purchase_option_estimate": purchase_option_estimate,
            "advisor_message_form": advisor_message_form,
            "advisor_messages": dossier.advisor_messages.all(),
        },
    )


"""Démarre une demande d'achat ou de LLD pour un véhicule donné."""


@login_required
@require_POST
def start_dossier(request, vehicle_pk, application_type):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)

    if application_type not in [
        Dossier.ApplicationType.SALE,
        Dossier.ApplicationType.LLD,
    ]:
        return redirect("vehicle_detail", pk=vehicle.pk)

    if (
        application_type == Dossier.ApplicationType.SALE
        and vehicle.offer_type
        not in [
            Vehicle.OfferType.SALE,
            Vehicle.OfferType.BOTH,
        ]
    ):
        return redirect("vehicle_detail", pk=vehicle.pk)

    if (
        application_type == Dossier.ApplicationType.LLD
        and vehicle.offer_type
        not in [
            Vehicle.OfferType.LLD,
            Vehicle.OfferType.BOTH,
        ]
    ):
        return redirect("vehicle_detail", pk=vehicle.pk)

    # Si un dossier actif existe déjà pour ce véhicule et ce type de demande,
    # on le réutilise pour éviter les doublons côté client.
    dossier = (
        Dossier.objects.filter(
            customer=request.user,
            vehicle=vehicle,
            application_type=application_type,
            status__in=ACTIVE_DOSSIER_STATUSES,
        )
        .order_by("-created_at")
        .first()
    )

    if dossier is None:
        dossier = Dossier.objects.create(
            customer=request.user,
            vehicle=vehicle,
            application_type=application_type,
            status=Dossier.Status.DRAFT,
        )

        DossierStatusHistory.objects.create(
            dossier=dossier,
            old_status=Dossier.Status.DRAFT,
            new_status=Dossier.Status.DRAFT,
            changed_by=request.user,
            comment="Création de la demande",
        )

    return redirect("dossier_detail", pk=dossier.pk)


"""Permet au client de compléter ses informations et déposer ses justificatifs."""


@login_required
def complete_dossier(request, pk):
    dossier = get_object_or_404(
        Dossier.objects.select_related(
            "vehicle",
            "customer",
        ).prefetch_related("documents"),
        pk=pk,
        customer=request.user,
    )

    profile, _ = ClientProfile.objects.get_or_create(user=request.user)

    required_document_types = REQUIRED_DOCUMENTS_BY_APPLICATION_TYPE.get(
        dossier.application_type,
        [],
    )

    uploaded_document_types = set(
        dossier.documents.values_list(
            "document_type",
            flat=True,
        )
    )

    required_documents_count = len(required_document_types)

    uploaded_documents_count = len(
        uploaded_document_types.intersection(required_document_types)
    )

    # La barre de progression du dossier est calculée
    # à partir des documents obligatoires.
    #
    # Exemple : pour une LLD avec 6 documents attendus,
    # 3 documents déposés donnent 50 %.
    completion_percentage = 0

    if required_documents_count:
        completion_percentage = round(
            uploaded_documents_count
            / required_documents_count
            * 100
        )

    is_dossier_complete = (
        required_documents_count > 0
        and uploaded_documents_count == required_documents_count
    )

    # Les informations générales sont modifiables
    # uniquement tant que le dossier est en brouillon.
    can_edit_dossier = dossier.status == Dossier.Status.DRAFT

    vehicle_monthly_price = dossier.vehicle.price_monthly or Decimal("0")
    estimated_location_total = Decimal("0")
    purchase_option_estimate = None

    if (
        dossier.application_type == Dossier.ApplicationType.LLD
        and dossier.lld_duration_months
    ):
        estimated_location_total = (
            vehicle_monthly_price * dossier.lld_duration_months
        )

        if dossier.vehicle.price_sale:
            purchase_option_estimate = (
                dossier.vehicle.price_sale - estimated_location_total
            )

            if purchase_option_estimate < 0:
                purchase_option_estimate = Decimal("0")

    document_upload_errors = {}

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save_information":
            # Après soumission, les données du dossier
            # ne peuvent plus être modifiées par le client.
            if not can_edit_dossier:
                return redirect("dossier_detail", pk=dossier.pk)

            form = DossierCompletionForm(
                request.POST,
                instance=dossier,
            )

            if form.is_valid():
                dossier = form.save(commit=False)

                # La date de consentement est enregistrée
                # uniquement au premier accord.
                if (
                    dossier.data_processing_consent
                    and not dossier.data_processing_consent_at
                ):
                    dossier.data_processing_consent_at = timezone.now()

                dossier.save()

                return redirect(
                    "complete_dossier",
                    pk=dossier.pk,
                )

        elif action == "upload_document":
            form = DossierCompletionForm(instance=dossier)

            document_type = request.POST.get("document_type")
            uploaded_file = request.FILES.get("file")

            existing_document = dossier.documents.filter(
                document_type=document_type
            ).first()

            # En brouillon, le client peut déposer ou remplacer
            # les justificatifs nécessaires.
            #
            # Après soumission, il ne peut remplacer
            # qu'un document explicitement refusé.
            can_upload_document = can_edit_dossier

            replacing_rejected_document = (
                existing_document is not None
                and existing_document.validation_status
                == Document.ValidationStatus.REJECTED
                and can_replace_rejected_document(
                    dossier,
                    document_type,
                )
            )

            if replacing_rejected_document:
                can_upload_document = True

            if not can_upload_document:
                return redirect("dossier_detail", pk=dossier.pk)

            upload_form = DocumentUploadForm(
                {
                    "document_type": document_type,
                },
                {
                    "file": uploaded_file,
                },
                allowed_document_types=[
                    (doc_type, doc_type)
                    for doc_type in required_document_types
                ],
            )

            if upload_form.is_valid():
                Document.objects.update_or_create(
                    dossier=dossier,
                    document_type=upload_form.cleaned_data[
                        "document_type"
                    ],
                    defaults={
                        "file": upload_form.cleaned_data["file"],
                        "validation_status": (
                            Document.ValidationStatus.PENDING
                        ),
                        "rejection_reason": "",
                        "validated_at": None,
                    },
                )

                # Lorsqu'un document refusé est remplacé,
                # le dossier repasse en instruction
                # et l'événement est enregistré dans l'historique.
                if replacing_rejected_document:
                    old_status = dossier.status

                    dossier.status = Dossier.Status.UNDER_REVIEW
                    dossier.reviewed_at = None

                    dossier.save(
                        update_fields=[
                            "status",
                            "reviewed_at",
                            "updated_at",
                        ]
                    )

                    document_label = dict(
                        Document.DocumentType.choices
                    ).get(
                        document_type,
                        document_type,
                    )

                    DossierStatusHistory.objects.create(
                        dossier=dossier,
                        old_status=old_status,
                        new_status=Dossier.Status.UNDER_REVIEW,
                        changed_by=request.user,
                        comment=(
                            "Remplacement par le client "
                            f"du document refusé : {document_label}"
                        ),
                    )

                return redirect(
                    "complete_dossier",
                    pk=dossier.pk,
                )

            document_upload_errors[document_type] = (
                upload_form.errors
            )

        elif action == "submit_dossier":
            form = DossierCompletionForm(instance=dossier)

            if (
                is_dossier_complete
                and dossier.status == Dossier.Status.DRAFT
            ):
                old_status = dossier.status

                dossier.status = Dossier.Status.SUBMITTED
                dossier.submitted_at = timezone.now()

                dossier.save(
                    update_fields=[
                        "status",
                        "submitted_at",
                        "updated_at",
                    ]
                )

                DossierStatusHistory.objects.create(
                    dossier=dossier,
                    old_status=old_status,
                    new_status=dossier.status,
                    changed_by=request.user,
                    comment=(
                        "Dossier soumis par le client "
                        "après dépôt des documents"
                    ),
                )

                return redirect(
                    "dossier_detail",
                    pk=dossier.pk,
                )

        else:
            form = DossierCompletionForm(instance=dossier)

    else:
        form = DossierCompletionForm(instance=dossier)

    return render(
        request,
        "dossiers/complete_dossier.html",
        {
            "dossier": dossier,
            "profile": profile,
            "form": form,
            "required_document_types": required_document_types,
            "completion_percentage": completion_percentage,
            "document_upload_errors": document_upload_errors,
            "is_dossier_complete": is_dossier_complete,
            "can_edit_dossier": can_edit_dossier,
            "vehicle_monthly_price": vehicle_monthly_price,
            "estimated_location_total": estimated_location_total,
            "purchase_option_estimate": purchase_option_estimate,
        },
    )


"""Soumet directement un dossier brouillon et historise le changement de statut."""


@login_required
@require_POST
def submit_dossier(request, pk):
    dossier = get_object_or_404(
        Dossier,
        pk=pk,
        customer=request.user,
        status=Dossier.Status.DRAFT,
    )

    old_status = dossier.status

    dossier.status = Dossier.Status.SUBMITTED
    dossier.submitted_at = timezone.now()

    dossier.save(
        update_fields=[
            "status",
            "submitted_at",
            "updated_at",
        ]
    )

    DossierStatusHistory.objects.create(
        dossier=dossier,
        old_status=old_status,
        new_status=dossier.status,
        changed_by=request.user,
        comment="Demande confirmée par le client",
    )

    return redirect(
        "dossier_detail",
        pk=dossier.pk,
    )


"""Supprime un dossier uniquement s'il appartient au client et reste en brouillon."""


@login_required
@require_POST
def delete_dossier(request, pk):
    dossier = get_object_or_404(
        Dossier,
        pk=pk,
        customer=request.user,
        status=Dossier.Status.DRAFT,
    )

    dossier.delete()

    return redirect("accounts:espace_client")


"""Retourne un document uniquement si le client connecté en est propriétaire."""


@login_required
def document_download(request, pk):
    document = get_object_or_404(
        Document.objects.select_related(
            "dossier",
            "dossier__customer",
        ),
        pk=pk,
        dossier__customer=request.user,
    )

    return FileResponse(
        document.file.open("rb"),
        as_attachment=False,
        filename=document.file.name.split("/")[-1],
    )