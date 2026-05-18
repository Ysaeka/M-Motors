from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ClientSignUpForm


@login_required
def espace_client(request):
    return render(request, "accounts/espace_client.html")


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