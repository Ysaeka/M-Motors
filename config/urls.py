from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts.forms import BrevoPasswordResetForm
from core.views import contact, healthcheck, home, mentions_legales


urlpatterns = [
    path("", home, name="home"),
    path("contact/", contact, name="contact"),
    path("health/", healthcheck, name="healthcheck"),
    path("catalog/", include("catalog.urls")),
    path("back-office/", include("backoffice.urls")),
    path("", include("accounts.urls")),

    # Route personnalisée pour la demande de réinitialisation.
    # On garde la vue native Django, mais on remplace le formulaire par notre formulaire Brevo afin d'envoyer l'email via l'API Brevo et non via SMTP.
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(form_class=BrevoPasswordResetForm),
        name="password_reset",
    ),

    # Routes d'authentification Django :
    # login, logout, password_reset_done, password_reset_confirm,
    # password_reset_complete, etc.
    path("accounts/", include("django.contrib.auth.urls")),

    path("admin/", admin.site.urls),
    path("dossiers/", include("dossiers.urls")),
    path("mentions-legales/", mentions_legales, name="mentions_legales"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)