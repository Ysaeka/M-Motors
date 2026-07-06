from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import get_object_or_404, render

from dossiers.models import Option

from .models import Vehicle


"""Affiche le catalogue avec filtres, budget, tri et pagination."""
def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by("-created_at")

    offer_type = request.GET.get("offer_type")
    budget_max = request.GET.get("budget_max")
    brand = request.GET.get("brand")
    fuel_types = request.GET.getlist("fuel_type")
    gearboxes = request.GET.getlist("gearbox")
    category = request.GET.get("category")
    sort = request.GET.get("sort", "newest")

    if offer_type in [Vehicle.OfferType.SALE, Vehicle.OfferType.LLD]:
        vehicles = vehicles.filter(offer_type=offer_type)

    if brand:
        vehicles = vehicles.filter(brand=brand)
    
    if category:
        vehicles = vehicles.filter(category=category)

    if fuel_types:
        vehicles = vehicles.filter(fuel_type__in=fuel_types)

    if gearboxes:
        vehicles = vehicles.filter(gearbox__in=gearboxes)

    # Le filtre budget dépend du type d'offre :
    # achat = prix de vente maximum, LLD = mensualité maximum.
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

    # Si le budget reçu dans l'URL est incohérent, on revient à une valeur par défaut.
    try:
        budget_value = float(budget_max)

        if budget_value < budget_min or budget_value > budget_max_limit:
            budget_value = default_budget
            budget_max = str(default_budget)

        if offer_type == Vehicle.OfferType.LLD:
            vehicles = vehicles.filter(price_monthly__lte=budget_value)
        elif offer_type == Vehicle.OfferType.SALE:
            vehicles = vehicles.filter(price_sale__lte=budget_value)

    except ValueError:
        budget_value = default_budget
        budget_max = str(default_budget)

    brands = Vehicle.objects.values_list("brand", flat=True).distinct().order_by("brand")

    categories = (
    Vehicle.objects.exclude(category="")
    .values_list("category", flat=True)
    .distinct()
    .order_by("category")
    )

    # Le tri garde les valeurs nulles en fin de liste pour éviter de mélanger les véhicules achat et LLD lorsqu'un prix n'existe pas.
    if sort == "price_sale_asc":
        vehicles = vehicles.order_by(F("price_sale").asc(nulls_last=True), "-created_at")
    elif sort == "price_sale_desc":
        vehicles = vehicles.order_by(F("price_sale").desc(nulls_last=True), "-created_at")
    elif sort == "price_monthly_asc":
        vehicles = vehicles.order_by(F("price_monthly").asc(nulls_last=True), "-created_at")
    elif sort == "price_monthly_desc":
        vehicles = vehicles.order_by(F("price_monthly").desc(nulls_last=True), "-created_at")
    else:
        sort = "newest"
        vehicles = vehicles.order_by("-created_at")

    # On conserve les filtres et le tri lors du changement de page.
    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_string = query_params.urlencode()

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
            "categories": categories,
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
            "selected_sort": sort,
            "query_string": query_string,
        },
    )

"""Affiche la fiche détaillée d'un véhicule."""
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    # Les options LLD affichées sont des services inclus dans l'offre et non des options payantes à sélectionner par le client.
    lld_options = Option.objects.none()
    if vehicle.has_lld_options:
        lld_options = Option.objects.filter(
            is_active=True,
            is_default_in_lld=True,
        ).order_by("name")

    return render(
        request,
        "catalog/vehicle_detail.html",
        {
            "vehicle": vehicle,
            "lld_options": lld_options,
        },
    )