from django.core.mail import send_mail
from django.conf import settings
from django.test import TestCase

class EmailTest(TestCase):

    def test_send_email(self):
        send_mail(
            subject="TEST EMAIL NGA DJANGO",
            message="Nëse ky email vjen, konfigurimi funksionon.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
