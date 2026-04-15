from django.http import HttpResponse, JsonResponse


def home(request):
    return HttpResponse("M Motors - application en ligne")


def healthcheck(request):
    return JsonResponse({"status": "ok"})
