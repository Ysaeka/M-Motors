from unittest.mock import MagicMock, patch
from urllib.error import URLError

from django.test import TestCase, override_settings
from django.urls import reverse

from core.email import send_brevo_email


class CoreViewsTests(TestCase):
    def test_home_page_returns_200(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")

    def test_healthcheck_returns_ok(self):
        response = self.client.get(reverse("healthcheck"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})

    def test_contact_page_returns_200(self):
        response = self.client.get(reverse("contact"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/contact.html")

    @patch("core.views.send_brevo_email")
    def test_contact_form_redirects_when_email_is_sent(self, mock_send_brevo_email):
        mock_send_brevo_email.return_value = True

        response = self.client.post(
            reverse("contact"),
            {
                "name": "Client Test",
                "email": "client@example.com",
                "phone": "0600000000",
                "message": "Bonjour, je souhaite avoir des informations.",
            },
        )

        self.assertRedirects(response, reverse("contact"))
        mock_send_brevo_email.assert_called_once()

    @patch("core.views.send_brevo_email")
    def test_contact_form_redirects_when_email_fails(self, mock_send_brevo_email):
        mock_send_brevo_email.return_value = False

        response = self.client.post(
            reverse("contact"),
            {
                "name": "Client Test",
                "email": "client@example.com",
                "phone": "",
                "message": "Message de test",
            },
        )

        self.assertRedirects(response, reverse("contact"))
        mock_send_brevo_email.assert_called_once()

    def test_mentions_legales_page_returns_200(self):
        response = self.client.get(reverse("mentions_legales"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/mentions_legales.html")


class BrevoEmailTests(TestCase):
    @override_settings(BREVO_API_KEY="")
    def test_send_brevo_email_returns_false_without_api_key(self):
        result = send_brevo_email(
            subject="Test",
            message="Message de test",
            recipient_email="client@example.com",
        )

        self.assertFalse(result)

    @override_settings(
        BREVO_API_KEY="fake-api-key",
        BREVO_SENDER_NAME="M Motors",
        BREVO_SENDER_EMAIL="contact@example.com",
    )
    @patch("core.email.url_request.urlopen")
    def test_send_brevo_email_returns_true_on_success(self, mock_urlopen):
        response_mock = MagicMock()
        response_mock.status = 201
        mock_urlopen.return_value.__enter__.return_value = response_mock

        result = send_brevo_email(
            subject="Test",
            message="Message de test",
            recipient_email="client@example.com",
            recipient_name="Client Test",
        )

        self.assertTrue(result)
        mock_urlopen.assert_called_once()

    @override_settings(
        BREVO_API_KEY="fake-api-key",
        BREVO_SENDER_NAME="M Motors",
        BREVO_SENDER_EMAIL="contact@example.com",
    )
    @patch("core.email.url_request.urlopen")
    def test_send_brevo_email_returns_false_on_error_status(self, mock_urlopen):
        response_mock = MagicMock()
        response_mock.status = 500
        mock_urlopen.return_value.__enter__.return_value = response_mock

        result = send_brevo_email(
            subject="Test",
            message="Message de test",
            recipient_email="client@example.com",
        )

        self.assertFalse(result)

    @override_settings(
        BREVO_API_KEY="fake-api-key",
        BREVO_SENDER_NAME="M Motors",
        BREVO_SENDER_EMAIL="contact@example.com",
    )
    @patch("core.email.url_request.urlopen")
    def test_send_brevo_email_returns_false_on_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Erreur API Brevo")

        result = send_brevo_email(
            subject="Test",
            message="Message de test",
            recipient_email="client@example.com",
        )

        self.assertFalse(result)