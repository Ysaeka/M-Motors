from functools import wraps

from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from catalog.models import Vehicle
from core.email import send_brevo_email
from dossiers.models import (
    Document,
    Dossier,
    DossierAdvisorMessage,
    DossierStatusHistory,
)

from .forms import VehicleForm


def backoffice_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        is_commercial = user.groups.filter(name="Commercial").exists()

        if user.is_superuser or is_commercial:
            return view_func(request, *args, **kwargs)

        raise PermissionDenied

    return login_required(wrapper)


def build_dossier_url(request, dossier):
    path = reverse("dossier_detail", args=[dossier.pk])

    if settings.SITE_URL:
        return f"{settings.SITE_URL.rstrip('/')}{path}"

    return request.build_absolute_uri(path)


def notify_customer_status_change(request, dossier):
    customer_email = dossier.customer.email

    if not customer_email:
        return

    dossier_url = build_dossier_url(request, dossier)

    send_brevo_email(
        subject="M Motors - Mise à jour de votre dossier",
        message=(
            "Bonjour,\n\n"
            "Le statut de votre dossier M Motors a été mis à jour.\n\n"
            f"Nouveau statut : {dossier.get_status_display()}\n\n"
            "Vous pouvez consulter le détail de votre dossier "
            "depuis votre espace client :\n"
            f"{dossier_url}\n\n"
            "Cordialement,\n"
            "L’équipe M Motors"
        ),
        recipient_email=customer_email,
        recipient_name=(
            dossier.customer.get_full_name()
            or dossier.customer.username
        ),
    )


def notify_customer_document_rejected(request, dossier, document):
    customer_email = dossier.customer.email

    if not customer_email:
        return

    dossier_url = build_dossier_url(request, dossier)

    send_brevo_email(
        subject="M Motors - Document refusé",
        message=(
            "Bonjour,\n\n"
            "Un document ajouté à votre dossier M Motors a été refusé.\n\n"
            f"Document concerné : {document.get_document_type_display()}\n"
            f"Motif : "
            f"{document.rejection_reason or 'Document non conforme.'}\n\n"
            "Vous pouvez consulter votre dossier et déposer "
            "un nouveau document depuis votre espace client :\n"
            f"{dossier_url}\n\n"
            "Cordialement,\n"
            "L’équipe M Motors"
        ),
        recipient_email=customer_email,
        recipient_name=(
            dossier.customer.get_full_name()
            or dossier.customer.username
        ),
    )


def synchronize_vehicle_status(dossier):
    """
    Synchronise la disponibilité du véhicule avec le statut du dossier.

    Le véhicule est verrouillé pendant la transaction afin que son statut
    ne puisse pas être modifié simultanément par une autre opération.

    Règles :
    - dossier soumis ou en instruction : véhicule réservé ;
    - demande d'achat acceptée : véhicule vendu ;
    - demande LLD acceptée : véhicule loué ;
    - dossier refusé : véhicule de nouveau disponible si aucun autre
      dossier actif ou accepté ne concerne le véhicule.
    """
    vehicle = Vehicle.objects.select_for_update().get(
        pk=dossier.vehicle_id
    )

    if dossier.status in [
        Dossier.Status.SUBMITTED,
        Dossier.Status.UNDER_REVIEW,
    ]:
        new_status = Vehicle.AvailabilityStatus.RESERVED

    elif dossier.status == Dossier.Status.APPROVED:
        if dossier.application_type == Dossier.ApplicationType.SALE:
            new_status = Vehicle.AvailabilityStatus.SOLD
        else:
            new_status = Vehicle.AvailabilityStatus.RENTED

    elif dossier.status == Dossier.Status.REJECTED:
        # Cette vérification protège également les anciennes données
        # qui auraient pu contenir plusieurs dossiers sur un même véhicule.
        other_approved_dossier = (
            Dossier.objects.filter(
                vehicle_id=vehicle.pk,
                status=Dossier.Status.APPROVED,
            )
            .exclude(pk=dossier.pk)
            .order_by("-reviewed_at", "-updated_at")
            .first()
        )

        if other_approved_dossier:
            if (
                other_approved_dossier.application_type
                == Dossier.ApplicationType.SALE
            ):
                new_status = Vehicle.AvailabilityStatus.SOLD
            else:
                new_status = Vehicle.AvailabilityStatus.RENTED

        else:
            other_active_dossier_exists = (
                Dossier.objects.filter(
                    vehicle_id=vehicle.pk,
                    status__in=[
                        Dossier.Status.SUBMITTED,
                        Dossier.Status.UNDER_REVIEW,
                    ],
                )
                .exclude(pk=dossier.pk)
                .exists()
            )

            if other_active_dossier_exists:
                new_status = Vehicle.AvailabilityStatus.RESERVED
            else:
                new_status = Vehicle.AvailabilityStatus.AVAILABLE

    else:
        return

    if vehicle.availability_status != new_status:
        vehicle.availability_status = new_status
        vehicle.save(
            update_fields=[
                "availability_status",
                "updated_at",
            ]
        )


@backoffice_required
def dashboard(request):
    recent_dossiers = (
        Dossier.objects.select_related(
            "customer",
            "vehicle",
        )
        .order_by("-updated_at")[:5]
    )

    recent_activities = (
        DossierStatusHistory.objects.select_related(
            "dossier",
            "dossier__customer",
            "dossier__vehicle",
            "changed_by",
        )
        .order_by("-created_at")[:5]
    )

    context = {
        "total_dossiers": Dossier.objects.count(),
        "submitted_dossiers": Dossier.objects.filter(
            status=Dossier.Status.SUBMITTED
        ).count(),
        "under_review_dossiers": Dossier.objects.filter(
            status=Dossier.Status.UNDER_REVIEW
        ).count(),
        "approved_dossiers": Dossier.objects.filter(
            status=Dossier.Status.APPROVED
        ).count(),
        "rejected_dossiers": Dossier.objects.filter(
            status=Dossier.Status.REJECTED
        ).count(),
        "available_vehicles": Vehicle.objects.filter(
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE
        ).count(),
        "recent_dossiers": recent_dossiers,
        "recent_activities": recent_activities,
    }

    return render(
        request,
        "backoffice/dashboard.html",
        context,
    )


@backoffice_required
def dossier_list(request):
    status_filter = request.GET.get("status")

    dossiers = (
        Dossier.objects.select_related(
            "customer",
            "vehicle",
        )
        .order_by("-updated_at")
    )

    page_title = "Demandes en cours"

    if status_filter:
        dossiers = dossiers.filter(
            status=status_filter
        )

        if status_filter == Dossier.Status.SUBMITTED:
            page_title = "Dossiers à traiter"

        elif status_filter == Dossier.Status.APPROVED:
            page_title = "Dossiers validés"

    context = {
        "dossiers": dossiers,
        "status_filter": status_filter,
        "page_title": page_title,
        "submitted_dossiers": Dossier.objects.filter(
            status=Dossier.Status.SUBMITTED
        ).count(),
        "under_review_dossiers": Dossier.objects.filter(
            status=Dossier.Status.UNDER_REVIEW
        ).count(),
        "approved_dossiers": Dossier.objects.filter(
            status=Dossier.Status.APPROVED
        ).count(),
        "rejected_dossiers": Dossier.objects.filter(
            status=Dossier.Status.REJECTED
        ).count(),
    }

    return render(
        request,
        "backoffice/dossier_list.html",
        context,
    )


@backoffice_required
def message_list(request):
    messages = (
        DossierAdvisorMessage.objects.select_related(
            "dossier",
            "dossier__customer",
            "dossier__vehicle",
            "responded_by",
        )
        .order_by("-created_at")
    )

    context = {
        "messages": messages,
        "total_messages": DossierAdvisorMessage.objects.count(),
        "unanswered_messages": (
            DossierAdvisorMessage.objects.filter(
                advisor_response=""
            ).count()
        ),
        "answered_messages": (
            DossierAdvisorMessage.objects.exclude(
                advisor_response=""
            ).count()
        ),
    }

    return render(
        request,
        "backoffice/message_list.html",
        context,
    )


@backoffice_required
def client_list(request):
    dossiers = (
        Dossier.objects.select_related(
            "customer",
            "vehicle",
        )
        .order_by("-updated_at")
    )

    clients_by_id = {}

    for dossier in dossiers:
        customer = dossier.customer

        if customer.id not in clients_by_id:
            clients_by_id[customer.id] = {
                "customer": customer,
                "dossier_count": 0,
                "last_dossier": dossier,
            }

        clients_by_id[customer.id]["dossier_count"] += 1

    clients = clients_by_id.values()

    context = {
        "clients": clients,
        "total_clients": len(clients_by_id),
    }

    return render(
        request,
        "backoffice/client_list.html",
        context,
    )


@backoffice_required
def vehicle_list(request):
    sort = request.GET.get("sort", "brand")
    direction = request.GET.get("direction", "asc")

    allowed_sorts = {
        "reference": "reference",
        "brand": "brand",
        "category": "category",
        "year": "year",
        "mileage": "mileage",
        "offer_type": "offer_type",
        "price_sale": "price_sale",
        "price_monthly": "price_monthly",
        "availability_status": "availability_status",
    }

    sort_field = allowed_sorts.get(
        sort,
        "brand",
    )

    if direction == "desc":
        sort_field = f"-{sort_field}"

    vehicles = Vehicle.objects.order_by(
        sort_field,
        "model",
    )

    context = {
        "vehicles": vehicles,
        "sort": sort,
        "direction": direction,
        "total_vehicles": Vehicle.objects.count(),
        "available_vehicles": Vehicle.objects.filter(
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE
        ).count(),
        "unavailable_vehicles": Vehicle.objects.exclude(
            availability_status=Vehicle.AvailabilityStatus.AVAILABLE
        ).count(),
    }

    return render(
        request,
        "backoffice/vehicle_list.html",
        context,
    )


@backoffice_required
def vehicle_create(request):
    if request.method == "POST":
        form = VehicleForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            vehicle = form.save()

            django_messages.success(
                request,
                f"Le véhicule {vehicle.reference} a bien été ajouté.",
            )

            return redirect(
                "backoffice:vehicle_list"
            )

    else:
        form = VehicleForm()

    context = {
        "form": form,
        "page_title": "Ajouter un véhicule",
        "submit_label": "Ajouter le véhicule",
    }

    return render(
        request,
        "backoffice/vehicle_form.html",
        context,
    )


@backoffice_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
    )

    if request.method == "POST":
        switch_offer = request.POST.get(
            "switch_offer"
        )

        allowed_offer_types = [
            Vehicle.OfferType.SALE,
            Vehicle.OfferType.LLD,
            Vehicle.OfferType.BOTH,
        ]

        if switch_offer in allowed_offer_types:
            vehicle.offer_type = switch_offer
            vehicle.save(
                update_fields=[
                    "offer_type",
                    "updated_at",
                ]
            )

            django_messages.success(
                request,
                (
                    f"L'offre du véhicule "
                    f"{vehicle.reference} a bien été mise à jour."
                ),
            )

            return redirect(
                "backoffice:vehicle_update",
                pk=vehicle.pk,
            )

        form = VehicleForm(
            request.POST,
            request.FILES,
            instance=vehicle,
        )

        if form.is_valid():
            vehicle = form.save()

            django_messages.success(
                request,
                (
                    f"Le véhicule {vehicle.reference} "
                    "a bien été modifié."
                ),
            )

            return redirect(
                "backoffice:vehicle_list"
            )

    else:
        form = VehicleForm(
            instance=vehicle
        )

    context = {
        "form": form,
        "vehicle": vehicle,
        "page_title": (
            f"Modifier {vehicle.reference}"
        ),
        "submit_label": "Enregistrer les modifications",
    }

    return render(
        request,
        "backoffice/vehicle_form.html",
        context,
    )


@backoffice_required
def vehicle_switch_offer(
    request,
    pk,
    offer_type,
):
    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
    )

    if request.method != "POST":
        django_messages.error(
            request,
            "Action non autorisée.",
        )

        return redirect(
            "backoffice:vehicle_list"
        )

    allowed_offer_types = [
        Vehicle.OfferType.SALE,
        Vehicle.OfferType.LLD,
        Vehicle.OfferType.BOTH,
    ]

    if offer_type not in allowed_offer_types:
        django_messages.error(
            request,
            "Type d'offre invalide.",
        )

        return redirect(
            "backoffice:vehicle_list"
        )

    vehicle.offer_type = offer_type

    vehicle.save(
        update_fields=[
            "offer_type",
            "updated_at",
        ]
    )

    django_messages.success(
        request,
        (
            f"L'offre du véhicule "
            f"{vehicle.reference} a bien été mise à jour."
        ),
    )

    return redirect(
        "backoffice:vehicle_list"
    )


@backoffice_required
def dossier_detail(request, pk):
    dossier = get_object_or_404(
        Dossier.objects.select_related(
            "customer",
            "vehicle",
        ).prefetch_related(
            "documents",
            "advisor_messages",
            "status_history",
        ),
        pk=pk,
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_internal_note":
            new_note = request.POST.get(
                "internal_note",
                "",
            ).strip()

            if new_note:
                author = (
                    request.user.get_full_name()
                    or request.user.username
                )

                timestamp = (
                    timezone.localtime()
                    .strftime("%d/%m/%Y à %H:%M")
                )

                formatted_note = (
                    f"{timestamp} - {author}\n"
                    f"{new_note}"
                )

                if dossier.internal_note:
                    dossier.internal_note = (
                        f"{dossier.internal_note}\n\n"
                        f"{formatted_note}"
                    )
                else:
                    dossier.internal_note = formatted_note

                dossier.save(
                    update_fields=[
                        "internal_note",
                        "updated_at",
                    ]
                )

                django_messages.success(
                    request,
                    "Le commentaire interne a bien été ajouté.",
                )

            return redirect(
                "backoffice:dossier_detail",
                pk=dossier.pk,
            )

        if action == "respond_message":
            message_id = request.POST.get(
                "message_id"
            )

            advisor_response = request.POST.get(
                "advisor_response",
                "",
            ).strip()

            advisor_message = get_object_or_404(
                DossierAdvisorMessage,
                pk=message_id,
                dossier=dossier,
            )

            if advisor_response:
                advisor_message.advisor_response = (
                    advisor_response
                )
                advisor_message.responded_by = (
                    request.user
                )
                advisor_message.responded_at = (
                    timezone.now()
                )

                advisor_message.save(
                    update_fields=[
                        "advisor_response",
                        "responded_by",
                        "responded_at",
                    ]
                )

                customer_email = (
                    dossier.customer.email
                )

                if customer_email:
                    client_space_url = (
                        build_dossier_url(
                            request,
                            dossier,
                        )
                    )

                    send_brevo_email(
                        subject=(
                            "Une réponse a été apportée "
                            "à votre message"
                        ),
                        message=(
                            "Bonjour,\n\n"
                            "Une réponse a été apportée "
                            "à votre message concernant "
                            "votre dossier M Motors.\n\n"
                            "Vous pouvez la consulter "
                            "depuis votre espace client :\n"
                            f"{client_space_url}\n\n"
                            "Cordialement,\n"
                            "L’équipe M Motors"
                        ),
                        recipient_email=customer_email,
                        recipient_name=(
                            dossier.customer.get_full_name()
                            or dossier.customer.username
                        ),
                    )

                django_messages.success(
                    request,
                    (
                        "La réponse a bien été enregistrée "
                        "et le client a été notifié par email."
                    ),
                )

            return redirect(
                "backoffice:dossier_detail",
                pk=dossier.pk,
            )

        if action in [
            "validate_document",
            "reject_document",
        ]:
            document_id = request.POST.get(
                "document_id"
            )

            document = get_object_or_404(
                Document,
                pk=document_id,
                dossier=dossier,
            )

            if action == "validate_document":
                document.validation_status = (
                    Document.ValidationStatus.VALIDATED
                )

                document.rejection_reason = ""

                django_messages.success(
                    request,
                    "Le document a bien été validé.",
                )

            else:
                document.validation_status = (
                    Document.ValidationStatus.REJECTED
                )

                document.rejection_reason = (
                    "Document refusé depuis le back-office."
                )

                django_messages.success(
                    request,
                    "Le document a bien été refusé.",
                )

                notify_customer_document_rejected(
                    request,
                    dossier,
                    document,
                )

            document.validated_at = timezone.now()

            document.save(
                update_fields=[
                    "validation_status",
                    "rejection_reason",
                    "validated_at",
                ]
            )

            return redirect(
                "backoffice:dossier_detail",
                pk=dossier.pk,
            )

        old_status = dossier.status

        if action == "mark_under_review":
            new_status = (
                Dossier.Status.UNDER_REVIEW
            )

            comment = (
                "Dossier passé en cours d'instruction "
                "depuis le back-office."
            )

        elif action == "approve":
            new_status = Dossier.Status.APPROVED

            comment = (
                "Dossier validé depuis le back-office."
            )

        elif action == "reject":
            new_status = Dossier.Status.REJECTED

            comment = (
                "Dossier refusé depuis le back-office."
            )

        else:
            django_messages.error(
                request,
                "Action inconnue.",
            )

            return redirect(
                "backoffice:dossier_detail",
                pk=dossier.pk,
            )

        # Le changement de statut du dossier et celui du véhicule
        # sont enregistrés dans une même transaction.
        with transaction.atomic():
            dossier.status = new_status
            dossier.reviewed_at = timezone.now()

            dossier.save(
                update_fields=[
                    "status",
                    "reviewed_at",
                    "updated_at",
                ]
            )

            synchronize_vehicle_status(
                dossier
            )

            DossierStatusHistory.objects.create(
                dossier=dossier,
                old_status=old_status,
                new_status=dossier.status,
                changed_by=request.user,
                comment=comment,
            )

        notify_customer_status_change(
            request,
            dossier,
        )

        django_messages.success(
            request,
            (
                "Le statut du dossier "
                "a bien été mis à jour."
            ),
        )

        return redirect(
            "backoffice:dossier_detail",
            pk=dossier.pk,
        )

    context = {
        "dossier": dossier,
        "documents": dossier.documents.all(),
        "messages": dossier.advisor_messages.all(),
        "history": dossier.status_history.all(),
    }

    return render(
        request,
        "backoffice/dossier_detail.html",
        context,
    )