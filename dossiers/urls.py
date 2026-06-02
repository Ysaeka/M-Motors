from django.urls import path

from . import views

urlpatterns = [
    path("", views.dossier_list, name="dossier_list"),
    path("<int:pk>/", views.dossier_detail, name="dossier_detail"),
    path("<int:pk>/submit/", views.submit_dossier, name="submit_dossier"),
    path("<int:pk>/delete/", views.delete_dossier, name="delete_dossier"),
    path("start/<int:vehicle_pk>/<str:application_type>/", views.start_dossier, name="start_dossier"),
]