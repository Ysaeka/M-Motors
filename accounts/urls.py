from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("inscription/", views.signup, name="signup"),
    path("mon-espace/", views.espace_client, name="espace_client"),
    path("mon-profil/", views.profil, name="profil"),
]