# Create your views here.
from django.shortcuts import get_object_or_404, render

from .models import Vehicle


def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by("-created_at")
    return render(request, "catalog/vehicle_list.html", {"vehicles": vehicles})

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, "catalog/vehicle_detail.html", {"vehicle": vehicle})