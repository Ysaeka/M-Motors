from django.conf import settings
from django.contrib import messages
from core.email import send_brevo_email
from django.http import JsonResponse
from django.shortcuts import redirect, render

from catalog.models import Vehicle

"""Affiche la page d'accueil avec les marques et catégories disponibles."""
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

"""Point de contrôle utilisé par le monitoring pour vérifier que l'application répond."""
def healthcheck(request):
    return JsonResponse({"status": "ok"})

"""Gère l'affichage et l'envoi du formulaire de contact."""
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

        # Le formulaire contacte l'adresse interne M Motors via Brevo.
        # Le visiteur reçoit uniquement un message de confirmation à l'écran.

        email_sent = send_brevo_email(
            subject=f"Nouveau message de contact - {name}",
            message=(
                f"Nom : {name}\n"
                f"Email : {email}\n"
                f"Téléphone : {phone or 'Non renseigné'}\n\n"
                f"Message :\n{message}"
            ),
            recipient_email=settings.CONTACT_EMAIL,
            recipient_name="M Motors",
        )

        if not email_sent:
            messages.error(
                request,
                "Votre message n’a pas pu être envoyé. Merci de réessayer plus tard.",
            )
            return redirect("contact")
     

        messages.success(
            request,
            "Votre message a bien été envoyé. L’équipe M Motors vous répondra dans les 24h ouvrés.",
        )
        return redirect("contact")

    return render(request, "pages/contact.html")

"""Affiche la page des mentions légales du projet."""
def mentions_legales(request):
    return render(request, "pages/mentions_legales.html")