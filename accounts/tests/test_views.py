from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


User = get_user_model()


class ClientAuthViewTests(TestCase):
    """
    Tests des pages liées au compte client.

    Objectif :
    - vérifier que les pages importantes répondent correctement ;
    - vérifier que l'inscription fonctionne ;
    - vérifier que l'espace client est protégé ;
    - vérifier que la réinitialisation de mot de passe envoie bien un email.
    """

    def test_signup_page_is_accessible(self):
        """La page d'inscription doit être accessible à un visiteur."""
        response = self.client.get(reverse("accounts:signup"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_signup_creates_user_and_redirects_to_client_space(self):
        """
        Une inscription valide doit créer un utilisateur
        puis rediriger vers l'espace client.
        """
        response = self.client.post(
            reverse("accounts:signup"),
            data={
                "username": "clienttestview",
                "email": "clienttestview@example.com",
                "password1": "VoitureBleue!7842",
                "password2": "VoitureBleue!7842",
            },
        )

        self.assertRedirects(response, reverse("accounts:espace_client"))
        self.assertTrue(User.objects.filter(username="clienttestview").exists())

    def test_signup_logs_user_in(self):
        """
        Après inscription, l'utilisateur doit être connecté automatiquement.
        On vérifie cela en accédant à l'espace client juste après l'inscription.
        """
        self.client.post(
            reverse("accounts:signup"),
            data={
                "username": "clienttestlogin",
                "email": "clienttestlogin@example.com",
                "password1": "VoitureBleue!7842",
                "password2": "VoitureBleue!7842",
            },
        )

        response = self.client.get(reverse("accounts:espace_client"))

        self.assertEqual(response.status_code, 200)

    def test_client_space_redirects_anonymous_user_to_login(self):
        """
        Un visiteur non connecté ne doit pas accéder directement
        à l'espace client.
        """
        response = self.client.get(reverse("accounts:espace_client"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('accounts:espace_client')}",
        )

    def test_client_space_is_accessible_for_authenticated_user(self):
        """Un utilisateur connecté doit pouvoir accéder à son espace client."""
        user = User.objects.create_user(
            username="clienttestauth",
            email="clienttestauth@example.com",
            password="VoitureBleue!7842",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:espace_client"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/espace_client.html")

    def test_profile_redirects_anonymous_user_to_login(self):
        """
        La page profil est une page privée.
        Un utilisateur non connecté doit donc être redirigé vers la connexion.
        """
        login_url = reverse("login")
        profile_url = reverse("accounts:profil")

        response = self.client.get(profile_url)

        self.assertRedirects(
            response,
            f"{login_url}?next={profile_url}",
        )

    def test_profile_is_accessible_for_authenticated_user(self):
        """Un utilisateur connecté doit pouvoir accéder à sa page profil."""
        user = User.objects.create_user(
            username="clientprofile",
            email="clientprofile@example.com",
            password="VoitureBleue!7842",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:profil"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profil.html")

    def test_authenticated_user_can_update_profile(self):
        """
        Un utilisateur connecté doit pouvoir modifier ses informations personnelles.

        On vérifie à la fois :
        - les champs du modèle User ;
        - les champs du profil client lié.
        """
        user = User.objects.create_user(
            username="clientupdate",
            email="old@example.com",
            password="VoitureBleue!7842",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:profil"),
            data={
                "first_name": "Ysaeka",
                "last_name": "Falletta",
                "email": "ysaeka@example.com",
                "phone": "0600000000",
                "address": "10 rue du Test",
            },
        )

        self.assertRedirects(response, reverse("accounts:profil"))

        user.refresh_from_db()
        self.assertEqual(user.first_name, "Ysaeka")
        self.assertEqual(user.last_name, "Falletta")
        self.assertEqual(user.email, "ysaeka@example.com")
        self.assertEqual(user.client_profile.phone, "0600000000")
        self.assertEqual(user.client_profile.address, "10 rue du Test")

    def test_login_page_contains_password_reset_link(self):
        """
        La page de connexion doit proposer un lien "mot de passe oublié".

        Ce test sécurise l'accès utilisateur à la fonctionnalité
        de réinitialisation.
        """
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("password_reset"))

    def test_password_reset_page_is_accessible(self):
        """
        La page de demande de réinitialisation doit être accessible.

        C'est la page où l'utilisateur saisit son adresse email.
        """
        response = self.client.get(reverse("password_reset"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_form.html")

    def test_password_reset_done_page_is_accessible(self):
        """
        La page de confirmation doit être accessible.

        Django affiche cette page même si l'email n'existe pas,
        pour ne pas révéler si un compte est présent en base.
        """
        response = self.client.get(reverse("password_reset_done"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_reset_done.html")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="contact@m-motors.local",
    )
    def test_password_reset_sends_email_for_existing_user(self):
        """
        Si l'email correspond à un utilisateur existant,
        Django doit générer un email de réinitialisation.

        Le backend locmem garde l'email en mémoire pendant le test.
        Cela permet de vérifier l'envoi sans envoyer de vrai email.
        """
        User.objects.create_user(
            username="clientreset",
            email="clientreset@example.com",
            password="VoitureBleue!7842",
        )

        response = self.client.post(
            reverse("password_reset"),
            data={"email": "clientreset@example.com"},
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Réinitialisation", mail.outbox[0].subject)
        self.assertIn("clientreset@example.com", mail.outbox[0].to)