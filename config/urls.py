from django.contrib import admin
from django.urls import path
from core.views import home, healthcheck

urlpatterns = [
    path("", home, name="home"),
    path("health/", healthcheck, name="healthcheck"),
    path("admin/", admin.site.urls),
]