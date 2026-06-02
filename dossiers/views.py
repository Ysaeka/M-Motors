from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from catalog.models import Vehicle

from .models import Dossier, DossierStatusHistory


ACTIVE_DOSSIER_STATUSES = [
    Dossier.Status.DRAFT,
    Dossier.Status.SUBMITTED,
    Dossier.Status.UNDER_REVIEW,
]


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


@login_required
def dossier_detail(request, pk):
    dossier = get_object_or_404(
        Dossier.objects.select_related("vehicle", "customer").prefetch_related(
            "options",
            "documents",
            "status_history",
        ),
        pk=pk,
        customer=request.user,
    )

    return render(
        request,
        "dossiers/dossier_detail.html",
        {
            "dossier": dossier,
        },
    )


@login_required
def start_dossier(request, vehicle_pk, application_type):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)

    if application_type not in [
        Dossier.ApplicationType.SALE,
        Dossier.ApplicationType.LLD,
    ]:
        return redirect("vehicle_detail", pk=vehicle.pk)

    if application_type == Dossier.ApplicationType.SALE and vehicle.offer_type not in [
        Vehicle.OfferType.SALE,
        Vehicle.OfferType.BOTH,
    ]:
        return redirect("vehicle_detail", pk=vehicle.pk)

    if application_type == Dossier.ApplicationType.LLD and vehicle.offer_type not in [
        Vehicle.OfferType.LLD,
        Vehicle.OfferType.BOTH,
    ]:
        return redirect("vehicle_detail", pk=vehicle.pk)

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
@login_required
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
    dossier.save(update_fields=["status", "submitted_at", "updated_at"])

    DossierStatusHistory.objects.create(
        dossier=dossier,
        old_status=old_status,
        new_status=dossier.status,
        changed_by=request.user,
        comment="Demande confirmée par le client",
    )

    return redirect("dossier_detail", pk=dossier.pk)


@login_required
def delete_dossier(request, pk):
    dossier = get_object_or_404(
        Dossier,
        pk=pk,
        customer=request.user,
        status=Dossier.Status.DRAFT,
    )

    dossier.delete()

    return redirect("accounts:espace_client")