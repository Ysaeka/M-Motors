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


class ClientProfileForm(forms.Form):
    first_name = forms.CharField(
        label="Prénom",
        required=False,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Votre prénom",
            }
        ),
    )
    last_name = forms.CharField(
        label="Nom",
        required=False,
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Votre nom",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Votre adresse email",
            }
        ),
    )
    phone = forms.CharField(
        label="Téléphone",
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Votre numéro de téléphone",
            }
        ),
    )
    address = forms.CharField(
        label="Adresse",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Votre adresse",
                "rows": 3,
            }
        ),
    )

    def __init__(self, *args, user=None, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.profile = profile

        if user and profile and not self.is_bound:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
            self.fields["phone"].initial = profile.phone
            self.fields["address"].initial = profile.address

    def save(self):
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]
        self.user.save()

        self.profile.phone = self.cleaned_data["phone"]
        self.profile.address = self.cleaned_data["address"]
        self.profile.save()

        return self.user