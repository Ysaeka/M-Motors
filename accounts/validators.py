import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins une majuscule."),
                code="password_no_uppercase",
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un chiffre."),
                code="password_no_digit",
            )

        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un caractère spécial."),
                code="password_no_special",
            )

    def get_help_text(self):
        return _(
            "Votre mot de passe doit contenir au moins une majuscule, "
            "un chiffre et un caractère spécial."
        )
    