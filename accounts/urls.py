from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("mon-espace/", views.espace_client, name="espace_client"),
]