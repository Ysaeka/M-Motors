# Create your views here.
from django.shortcuts import render

from .models import Vehicle


def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by("-created_at")
    return render(request, "catalog/vehicle_list.html", {"vehicles": vehicles})
