from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from catalog.models import Vehicle
from dossiers.models import Dossier, DossierStatusHistory


@staff_member_required
def dashboard(request):
    recent_dossiers = (
        Dossier.objects.select_related("customer", "vehicle")
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

    return render(request, "backoffice/dashboard.html", context)