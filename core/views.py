from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    return render(request, "pages/home.html")

def healthcheck(request):
    return JsonResponse({"status": "ok"})
