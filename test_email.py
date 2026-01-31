import os
import django
from django.conf import settings
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_email():
    try:
        print(f"Attempting to send email from {settings.EMAIL_HOST_USER}...")
        send_mail(
            'Test Subject',
            'Test message body.',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER], # send to self
            fail_silently=False,
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    test_email()
