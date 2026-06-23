from django.conf import settings
from django.contrib import messages
from core.email import send_brevo_email
from django.http import JsonResponse
from django.shortcuts import redirect, render

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

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

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