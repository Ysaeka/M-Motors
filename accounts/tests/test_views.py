from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class ClientAuthViewTests(TestCase):
    def test_signup_page_is_accessible(self):
        response = self.client.get(reverse("accounts:signup"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_signup_creates_user_and_redirects_to_client_space(self):
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
        response = self.client.get(reverse("accounts:espace_client"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('accounts:espace_client')}",
        )

    def test_client_space_is_accessible_for_authenticated_user(self):
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
        login_url = reverse("login")
        profile_url = reverse("accounts:profil")

        response = self.client.get(profile_url)

        self.assertRedirects(
            response,
            f"{login_url}?next={profile_url}",
        )

    def test_profile_is_accessible_for_authenticated_user(self):
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