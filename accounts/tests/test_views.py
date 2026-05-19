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