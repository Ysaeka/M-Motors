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

        vehicle, _ = Vehicle.objects.get_or_create(
            reference="MM-SEED-001",
            defaults={
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
        )

        dossier, created = Dossier.objects.get_or_create(
            customer=user,
            vehicle=vehicle,
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