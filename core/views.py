from django.http import JsonResponse
from django.shortcuts import render

from catalog.models import Vehicle


def home(request):
    brands = Vehicle.objects.values_list("brand", flat=True).distinct().order_by("brand")
    categories = (
        Vehicle.objects.exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    return render(
        request,
        "pages/home.html",
        {
            "brands": brands,
            "categories": categories,
        },
    )


def healthcheck(request):
    return JsonResponse({"status": "ok"})