from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ClientSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Nom d'utilisateur"
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control register-input",
                "placeholder": "Votre nom d'utilisateur",
            }
        )

        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control register-input",
                "placeholder": "Votre adresse email",
            }
        )

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control register-input",
                "placeholder": "Créer un mot de passe",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control register-input",
                "placeholder": "Confirmer le mot de passe",
            }
        )