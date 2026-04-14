from django.http import HttpResponse


def home(request):
    return HttpResponse("M Motors - application en ligne")
