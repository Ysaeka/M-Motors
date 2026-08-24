from django.test import TestCase

from accounts.forms import ClientSignUpForm


class ClientSignUpFormTests(TestCase):
    def test_form_is_valid_with_secure_password(self):
        form = ClientSignUpForm(
            data={
                "username": "clienttestform",
                "email": "clienttestform@example.com",
                "password1": "VoitureBleue!7842",
                "password2": "VoitureBleue!7842",
            }
        )

        self.assertTrue(form.is_valid())

    def test_form_is_invalid_when_passwords_do_not_match(self):
        form = ClientSignUpForm(
            data={
                "username": "clienttestform",
                "email": "clienttestform@example.com",
                "password1": "VoitureBleue!7842",
                "password2": "VoitureRouge!7842",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_is_invalid_without_uppercase(self):
        form = ClientSignUpForm(
            data={
                "username": "clienttestform",
                "email": "clienttestform@example.com",
                "password1": "voiturebleue!7842",
                "password2": "voiturebleue!7842",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_is_invalid_without_digit(self):
        form = ClientSignUpForm(
            data={
                "username": "clienttestform",
                "email": "clienttestform@example.com",
                "password1": "VoitureBleue!",
                "password2": "VoitureBleue!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_is_invalid_without_special_character(self):
        form = ClientSignUpForm(
            data={
                "username": "clienttestform",
                "email": "clienttestform@example.com",
                "password1": "VoitureBleue7842",
                "password2": "VoitureBleue7842",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)