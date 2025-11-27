# newsletter/utils.py
from django.core import signing
from django.urls import reverse
from django.conf import settings

SIGNER = signing.Signer(salt='newsletter-unsubscribe')

def generate_unsubscribe_url(subscriber, request=None):
    """
    Generates a signed unsubscribe URL for the subscriber.
    """
    token = SIGNER.sign(subscriber.pk)  # sign subscriber ID
    path = reverse("newsletter:unsubscribe_newsletter", kwargs={"uidb64": token})

    if request:
        return request.build_absolute_uri(path)

    # Use SITE_URL from settings for production
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    return f"{site_url}{path}"


def verify_unsubscribe_token(token):
    """
    Verifies a signed token and returns the subscriber ID.
    """
    try:
        subscriber_id = SIGNER.unsign(token)
        return subscriber_id
    except signing.BadSignature:
        return None
