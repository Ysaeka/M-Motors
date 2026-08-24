import json
from urllib import request as url_request
from urllib.error import HTTPError, URLError

from django.conf import settings


"""Envoie un email transactionnel via l'API Brevo.
    Retourne True si l'API accepte la demande d'envoi, sinon False.
    La fonction ne lève pas d'exception afin de laisser la vue gérer l'affichage d'un message utilisateur adapté.
    """
def send_brevo_email(subject, message, recipient_email, recipient_name=""):
    if not settings.BREVO_API_KEY:
        return False

    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [
            {
                "email": recipient_email,
                "name": recipient_name or recipient_email,
            }
        ],
        "subject": subject,
        "textContent": message,
    }

    data = json.dumps(payload).encode("utf-8")

    request = url_request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=data,
        headers={
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        },
        method="POST",
    )

    # Le timeout évite de bloquer la requête utilisateur si l'API Brevo ne répond pas.
    try:
        with url_request.urlopen(request, timeout=10) as response:
            return 200 <= response.status < 300
    except (HTTPError, URLError, TimeoutError):
        return False