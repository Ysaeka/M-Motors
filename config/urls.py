from django.contrib import admin
from django.urls import include, path

from core.views import home, healthcheck

urlpatterns = [
    path("", home, name="home"),
    path("health/", healthcheck, name="healthcheck"),
    path("catalog/", include("catalog.urls")),
    path("", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]