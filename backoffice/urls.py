from django.urls import path

from . import views

app_name = "backoffice"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dossiers/", views.dossier_list, name="dossier_list"),
    path("dossiers/<int:pk>/", views.dossier_detail, name="dossier_detail"),
]