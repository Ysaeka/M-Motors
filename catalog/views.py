from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Vehicle


def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by("-created_at")

    offer_type = request.GET.get("offer_type")
    budget_max = request.GET.get("budget_max")
    brand = request.GET.get("brand")
    fuel_types = request.GET.getlist("fuel_type")
    gearboxes = request.GET.getlist("gearbox")
    category = request.GET.get("category")

    if offer_type in [Vehicle.OfferType.SALE, Vehicle.OfferType.LLD]:
        vehicles = vehicles.filter(offer_type=offer_type)

    if brand:
        vehicles = vehicles.filter(brand=brand)
    
    if brand:
        vehicles = vehicles.filter(brand=brand)

    if category:
        vehicles = vehicles.filter(category=category)

    if fuel_types:
        vehicles = vehicles.filter(fuel_type__in=fuel_types)

    if gearboxes:
        vehicles = vehicles.filter(gearbox__in=gearboxes)

    if offer_type == Vehicle.OfferType.LLD:
        budget_label = "Mensualité max"
        budget_min = 100
        budget_max_limit = 1000
        budget_step = 10
        default_budget = 300
    else:
        budget_label = "Budget achat max"
        budget_min = 5000
        budget_max_limit = 50000
        budget_step = 500
        default_budget = 15000

    if not budget_max:
        budget_max = str(default_budget)

    try:
        budget_value = float(budget_max)
        if offer_type == Vehicle.OfferType.LLD:
            vehicles = vehicles.filter(price_monthly__lte=budget_value)
        elif offer_type == Vehicle.OfferType.SALE:
            vehicles = vehicles.filter(price_sale__lte=budget_value)
    except ValueError:
        budget_max = str(default_budget)

    brands = Vehicle.objects.values_list("brand", flat=True).distinct().order_by("brand")

    paginator = Paginator(vehicles, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "catalog/vehicle_list.html",
        {
            "vehicles": page_obj,
            "page_obj": page_obj,
            "brands": brands,
            "selected_offer_type": offer_type,
            "selected_budget_max": budget_max,
            "selected_brand": brand,
            "selected_category": category,
            "selected_fuel_types": fuel_types,
            "selected_gearboxes": gearboxes,
            "budget_label": budget_label,
            "budget_min": budget_min,
            "budget_max_limit": budget_max_limit,
            "budget_step": budget_step,
        },
    )


def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, "catalog/vehicle_detail.html", {"vehicle": vehicle})