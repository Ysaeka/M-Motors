from django.contrib import messages
from django.contrib.auth import login
from dossiers.models import Dossier
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import ClientProfile
from .forms import ClientProfileForm, ClientSignUpForm



@login_required
def espace_client(request):
    if request.user.is_superuser or request.user.groups.filter(name="Commercial").exists():
        return redirect("backoffice:dashboard")

    profile, _ = ClientProfile.objects.get_or_create(user=request.user)

    dossiers = (
        Dossier.objects.filter(customer=request.user)
        .select_related("vehicle")
        .order_by("-created_at")
    )

    return render(
        request,
        "accounts/espace_client.html",
        {
            "profile": profile,
            "dossiers": dossiers,
        },
    )

@login_required
def profil(request):
    profile, _ = ClientProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ClientProfileForm(request.POST, user=request.user, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a bien été mis à jour.")
            return redirect("accounts:profil")
    else:
        form = ClientProfileForm(user=request.user, profile=profile)

    return render(request, "accounts/profil.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = ClientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte client a bien été créé.")
            return redirect("accounts:espace_client")
    else:
        form = ClientSignUpForm()

    return render(request, "accounts/signup.html", {"form": form})