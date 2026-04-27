from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from catalog.models import Vehicle
from dossiers.models import Dossier, DossierStatusHistory, Option


class Command(BaseCommand):
    help = "Seed simple de données de test"

    def handle(self, *args, **options):
        User = get_user_model()

        user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        options_data = [
            {
                "code": "insurance_all_risk",
                "name": "Assurance tous risques",
                "description": "Couverture assurance complète du véhicule",
                "is_active": True,
                "is_default_in_lld": True,
                "monthly_price": 0,
            },
            {
                "code": "roadside_assistance",
                "name": "Assistance dépannage",
                "description": "Assistance en cas de panne ou incident",
                "is_active": True,
                "is_default_in_lld": True,
                "monthly_price": 0,
            },
            {
                "code": "maintenance_sav",
                "name": "Entretien et SAV",
                "description": "Entretien courant et service après-vente",
                "is_active": True,
                "is_default_in_lld": True,
                "monthly_price": 0,
            },
            {
                "code": "technical_control",
                "name": "Contrôle technique",
                "description": "Prise en charge du contrôle technique",
                "is_active": True,
                "is_default_in_lld": True,
                "monthly_price": 0,
            },
        ]

        created_options = []
        for option_data in options_data:
            option, _ = Option.objects.get_or_create(
                code=option_data["code"],
                defaults=option_data,
            )
            created_options.append(option)

        vehicles_data = [
            {
                "reference": "MM_REN_001",
                "brand": "Renault",
                "model": "Clea",
                "trim": "",
                "category": "Citadine",
                "year": 2020,
                "mileage": 45000,
                "fuel_type": Vehicle.FuelType.DIESEL,
                "gearbox": Vehicle.GearboxType.MANUAL,
                "price_sale": 12900.00,
                "price_monthly": 129.00,
                "description": "Citadine moderne et économique, idéale pour les trajets urbains et les déplacements quotidiens. Elle offre une conduite souple, une consommation maîtrisée et des équipements pratiques comme le Bluetooth et le régulateur de vitesse.",
                "offer_type": Vehicle.OfferType.BOTH,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_REN_002",
                "brand": "Renault",
                "model": "Captor",
                "trim": "",
                "category": "SUV",
                "year": 2019,
                "mileage": 52000,
                "fuel_type": Vehicle.FuelType.GASOLINE,
                "gearbox": Vehicle.GearboxType.AUTOMATIC,
                "price_sale": 15400.00,
                "price_monthly": 139.00,
                "description": "SUV compact polyvalent, parfait pour la ville comme pour les sorties en famille. Son habitacle spacieux, sa position de conduite surélevée et ses aides au stationnement en font un véhicule agréable au quotidien.",
                "offer_type": Vehicle.OfferType.SALE,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_REN_003",
                "brand": "Renault",
                "model": "Megan",
                "trim": "",
                "category": "Berline",
                "year": 2020,
                "mileage": 68000,
                "fuel_type": Vehicle.FuelType.DIESEL,
                "gearbox": Vehicle.GearboxType.AUTOMATIC,
                "price_sale": 14800.00,
                "price_monthly": 119.00,
                "description": "Berline confortable et élégante, pensée pour les conducteurs recherchant sobriété et confort sur route. Elle dispose d’un bon niveau d’équipement avec GPS, climatisation automatique et aide au stationnement.",
                "offer_type": Vehicle.OfferType.LLD,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_PEU_001",
                "brand": "Peugeot",
                "model": "228",
                "trim": "",
                "category": "Citadine",
                "year": 2021,
                "mileage": 39000,
                "fuel_type": Vehicle.FuelType.GASOLINE,
                "gearbox": Vehicle.GearboxType.MANUAL,
                "price_sale": 13700.00,
                "price_monthly": 119.00,
                "description": "Citadine dynamique au design moderne, parfaite pour les jeunes conducteurs ou un usage urbain. Son moteur souple et son écran tactile rendent chaque trajet plus agréable.",
                "offer_type": Vehicle.OfferType.BOTH,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_PEU_002",
                "brand": "Peugeot",
                "model": "318",
                "trim": "",
                "category": "Berline",
                "year": 2020,
                "mileage": 16500,
                "fuel_type": Vehicle.FuelType.HYBRID,
                "gearbox": Vehicle.GearboxType.MANUAL,
                "price_sale": 16500.00,
                "price_monthly": 149.00,
                "description": "Berline polyvalente appréciée pour son confort de conduite et sa faible consommation. Très bien équipée, elle convient aussi bien à la ville qu’aux longs trajets autoroutiers.",
                "offer_type": Vehicle.OfferType.LLD,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_PEU_003",
                "brand": "Peugeot",
                "model": "3009",
                "trim": "",
                "category": "SUV",
                "year": 2020,
                "mileage": 63000,
                "fuel_type": Vehicle.FuelType.DIESEL,
                "gearbox": Vehicle.GearboxType.AUTOMATIC,
                "price_sale": 21900.00,
                "price_monthly": 169.00,
                "description": "SUV élégant et haut de gamme, reconnu pour son confort, sa qualité intérieure et ses technologies embarquées. Une excellente option pour une famille recherchant un véhicule valorisant et pratique.",
                "offer_type": Vehicle.OfferType.BOTH,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_FOR_001",
                "brand": "Ford",
                "model": "Fiesto",
                "trim": "",
                "category": "Citadine",
                "year": 2019,
                "mileage": 47000,
                "fuel_type": Vehicle.FuelType.GASOLINE,
                "gearbox": Vehicle.GearboxType.MANUAL,
                "price_sale": 12600.00,
                "price_monthly": 119.00,
                "description": "Citadine nerveuse et agréable à conduire, très appréciée pour sa maniabilité et son confort. Un modèle compact parfait pour la ville avec un bon niveau d’équipement.",
                "offer_type": Vehicle.OfferType.SALE,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_FOR_002",
                "brand": "Ford",
                "model": "Focal",
                "trim": "",
                "category": "Berline",
                "year": 2020,
                "mileage": 54000,
                "fuel_type": Vehicle.FuelType.DIESEL,
                "gearbox": Vehicle.GearboxType.MANUAL,
                "price_sale": 15900.00,
                "price_monthly": 129.00,
                "description": "Berline compacte équilibrée, idéale pour les trajets quotidiens comme pour la route. Elle offre une bonne tenue de route, une faible consommation et un intérieur confortable.",
                "offer_type": Vehicle.OfferType.LLD,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_FOR_003",
                "brand": "Ford",
                "model": "Kaga",
                "trim": "",
                "category": "SUV",
                "year": 2021,
                "mileage": 66000,
                "fuel_type": Vehicle.FuelType.ELECTRIC,
                "gearbox": Vehicle.GearboxType.AUTOMATIC,
                "price_sale": 23400.00,
                "price_monthly": 159.00,
                "description": "SUV confortable et spacieux, pensé pour les familles et les conducteurs recherchant de la polyvalence. Il se distingue par son confort, son équipement complet et sa position de conduite agréable.",
                "offer_type": Vehicle.OfferType.BOTH,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_TOY_001",
                "brand": "Toyata",
                "model": "Yolo",
                "trim": "",
                "category": "Citadine",
                "year": 2021,
                "mileage": 16800,
                "fuel_type": Vehicle.FuelType.GASOLINE,
                "gearbox": Vehicle.GearboxType.MANUAL,
                "price_sale": 16800.00,
                "price_monthly": 129.00,
                "description": "Citadine hybride idéale pour la ville, réputée pour sa fiabilité et sa faible consommation. Très agréable en circulation urbaine, elle combine silence de fonctionnement et coût d’usage réduit.",
                "offer_type": Vehicle.OfferType.BOTH,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_TOY_002",
                "brand": "Toyata",
                "model": "Coriolis",
                "trim": "",
                "category": "Berline",
                "year": 2020,
                "mileage": 49000,
                "fuel_type": Vehicle.FuelType.HYBRID,
                "gearbox": Vehicle.GearboxType.AUTOMATIC,
                "price_sale": 21200.00,
                "price_monthly": 159.00,
                "description": "Berline moderne et efficiente, parfaite pour ceux qui recherchent confort, sobriété et fiabilité. Son moteur hybride assure une conduite fluide aussi bien en ville que sur route.",
                "offer_type": Vehicle.OfferType.SALE,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM_TOY_003",
                "brand": "Toyata",
                "model": "C-MP",
                "trim": "",
                "category": "SUV",
                "year": 2021,
                "mileage": 43000,
                "fuel_type": Vehicle.FuelType.ELECTRIC,
                "gearbox": Vehicle.GearboxType.MANUAL,
                "price_sale": 22700.00,
                "price_monthly": 179.00,
                "description": "SUV compact au design audacieux, très apprécié pour son confort et sa technologie hybride. Un modèle idéal pour se démarquer tout en maîtrisant sa consommation.",
                "offer_type": Vehicle.OfferType.LLD,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
            {
                "reference": "MM-SEED-001",
                "brand": "Renault",
                "model": "Clio",
                "trim": "Business",
                "category": "Citadine",
                "year": 2022,
                "mileage": 18000,
                "fuel_type": Vehicle.FuelType.HYBRID,
                "gearbox": Vehicle.GearboxType.AUTOMATIC,
                "price_sale": None,
                "price_monthly": 299.00,
                "description": "Véhicule de test pour seed",
                "offer_type": Vehicle.OfferType.LLD,
                "availability_status": Vehicle.AvailabilityStatus.AVAILABLE,
            },
        ]

        seed_vehicle = None
        for vehicle_data in vehicles_data:
            vehicle, _ = Vehicle.objects.get_or_create(
                reference=vehicle_data["reference"],
                defaults=vehicle_data,
            )
            if vehicle.reference == "MM-SEED-001":
                seed_vehicle = vehicle

        if seed_vehicle is None:
            seed_vehicle = Vehicle.objects.get(reference="MM-SEED-001")

        dossier, created = Dossier.objects.get_or_create(
            customer=user,
            vehicle=seed_vehicle,
            application_type=Dossier.ApplicationType.LLD,
            defaults={
                "status": Dossier.Status.SUBMITTED,
                "customer_note": "Dossier créé automatiquement par le seed",
                "internal_note": "Dossier de test",
            },
        )

        dossier.options.set(created_options)

        DossierStatusHistory.objects.get_or_create(
            dossier=dossier,
            old_status=Dossier.Status.DRAFT,
            new_status=Dossier.Status.SUBMITTED,
            defaults={
                "changed_by": user,
                "comment": "Création automatique via seed",
            },
        )

        self.stdout.write(self.style.SUCCESS("Seed terminé avec succès."))