from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from core.views import contact, home, healthcheck, mentions_legales

urlpatterns = [
    path("", home, name="home"),
    path("contact/", contact, name="contact"),
    path("health/", healthcheck, name="healthcheck"),
    path("catalog/", include("catalog.urls")),
    path("back-office/", include("backoffice.urls")),
    path("", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("dossiers/", include("dossiers.urls")),
    path("mentions-legales/", mentions_legales, name="mentions_legales"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)