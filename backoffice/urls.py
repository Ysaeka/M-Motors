from django.urls import path

from . import views

app_name = "backoffice"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dossiers/", views.dossier_list, name="dossier_list"),
    path("dossiers/<int:pk>/", views.dossier_detail, name="dossier_detail"),
    path("messages/", views.message_list, name="message_list"),
    path("clients/", views.client_list, name="client_list"),
    path("vehicules/", views.vehicle_list, name="vehicle_list"),
    path("vehicules/ajouter/", views.vehicle_create, name="vehicle_create"),
    path("vehicules/<int:pk>/modifier/", views.vehicle_update, name="vehicle_update"),
    path(
        "vehicules/<int:pk>/basculer/<str:offer_type>/",
        views.vehicle_switch_offer,
        name="vehicle_switch_offer",
    ),
]