from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def espace_client(request):
    return render(request, "accounts/espace_client.html")